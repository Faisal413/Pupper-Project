import json
import boto3
import uuid
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
kms_client = boto3.client('kms')

# Environment variables
DOGS_TABLE_NAME = os.environ['DOGS_TABLE_NAME']
IMAGES_BUCKET_NAME = os.environ['IMAGES_BUCKET_NAME']
KMS_KEY_ID = os.environ['KMS_KEY_ID']

# Get DynamoDB table
dogs_table = dynamodb.Table(DOGS_TABLE_NAME)

def handler(event, context):
    """
    Main handler for presigned URL upload process
    Handles two main endpoints:
    1. POST /upload/presigned - Generate presigned URL for image upload
    2. POST /upload/complete - Complete dog registration after image upload
    """
    try:
        logger.info(f"Upload handler received event: {json.dumps(event, default=str)}")
        
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # CORS headers for browser compatibility
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        }
        
        # Handle preflight CORS requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
        # Route requests to appropriate handlers
        if '/upload/presigned' in path and http_method == 'POST':
            # Step 1: Generate presigned URL for direct S3 upload
            return generate_presigned_url(event, cors_headers)
        elif '/upload/complete' in path and http_method == 'POST':
            # Step 2: Complete dog registration after image upload
            return complete_dog_registration(event, cors_headers)
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        logger.error(f"Error in upload handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Internal server error'})
        }

def generate_presigned_url(event, cors_headers):
    """
    STEP 1: Generate presigned URL for direct S3 upload
    
    This function:
    1. Validates the image file metadata (filename, size, type)
    2. Generates a unique S3 key for the image
    3. Creates a presigned URL that allows direct upload to S3
    4. Returns the URL and upload metadata to the frontend
    
    Frontend will use this URL to upload the image directly to S3
    """
    try:
        # Parse request body containing image metadata
        body = event.get('body', '')
        if not body:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        data = json.loads(body)
        
        # Validate required image metadata
        filename = data.get('filename')
        file_size = data.get('file_size')  # Size in bytes
        content_type = data.get('content_type')
        
        if not all([filename, file_size, content_type]):
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Missing required fields: filename, file_size, content_type'
                })
            }
        
        # Validate file size (max 50MB for this example)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if file_size > max_size:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': f'File too large. Maximum size is {max_size // (1024*1024)}MB'
                })
            }
        
        # Validate file type (only images)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if content_type not in allowed_types:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': f'Invalid file type. Allowed types: {allowed_types}'
                })
            }
        
        # Generate unique S3 key for the image
        file_extension = filename.split('.')[-1].lower()
        unique_filename = f"{str(uuid.uuid4())}.{file_extension}"
        s3_key = f"uploads/images/{unique_filename}"
        
        # Generate presigned URL for PUT operation (direct upload)
        # This URL allows the frontend to upload directly to S3
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': IMAGES_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': content_type,

            },
            ExpiresIn=3600,  # URL expires in 1 hour
            HttpMethod='PUT'
        )
        
        # Return presigned URL and metadata to frontend
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Presigned URL generated successfully',
                'upload_url': presigned_url,
                'upload_method': 'PUT',
                's3_key': s3_key,
                'expires_in': 3600,
                'instructions': {
                    'step1': 'Use PUT method to upload file to upload_url',
                    'step2': 'Set Content-Type header to the file content type',
                    'step3': 'After successful upload, call /upload/complete with dog data and s3_key'
                }
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Failed to generate presigned URL'})
        }

def complete_dog_registration(event, cors_headers):
    """
    STEP 2: Complete dog registration after image upload
    
    This function:
    1. Receives dog data and the S3 key of the uploaded image
    2. Validates that the image exists in S3
    3. Validates dog data (Labrador Retriever check, required fields)
    4. Encrypts sensitive data (dog name)
    5. Saves complete dog record to DynamoDB
    6. Returns success confirmation
    
    Called by frontend after successful image upload to S3
    """
    try:
        # Parse request body containing dog data and image reference
        body = event.get('body', '')
        if not body:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        data = json.loads(body)
        
        # Validate required dog data fields
        required_fields = ['shelter', 'city', 'state', 'dog_name', 'dog_species', 'dog_description']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': f'Missing required fields: {missing_fields}'
                })
            }
        
        # Get S3 key of uploaded image
        s3_key = data.get('s3_key')
        if not s3_key:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Missing s3_key - image must be uploaded first'
                })
            }
        
        # Verify image exists in S3
        try:
            s3_client.head_object(Bucket=IMAGES_BUCKET_NAME, Key=s3_key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'Image not found in S3. Please upload image first.'
                    })
                }
            raise
        
        # Validate dog species (only Labrador Retrievers)
        dog_species = data['dog_species'].lower()
        if 'labrador' not in dog_species and 'lab' not in dog_species:
            return {
                'statusCode': 422,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Only Labrador Retrievers are accepted',
                    'species_provided': data['dog_species']
                })
            }
        
        # Generate unique identifiers
        shelter_id = generate_shelter_id(data['shelter'], data['city'], data['state'])
        dog_id = str(uuid.uuid4())
        
        # Encrypt sensitive data (dog name) using KMS
        encrypted_dog_name = encrypt_dog_name(data['dog_name'])
        
        # Create complete dog record for database
        dog_record = {
            'shelter_id': shelter_id,
            'dog_id': dog_id,
            'shelter': data['shelter'],
            'city': data['city'],
            'state': data['state'],
            'encrypted_dog_name': encrypted_dog_name,
            'species': data['dog_species'],
            'description': data['dog_description'],
            'image_s3_key': s3_key,
            'image_url': f"https://{IMAGES_BUCKET_NAME}.s3.amazonaws.com/{s3_key}",
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields if provided
        if data.get('dog_birthday'):
            dog_record['dog_birthday'] = data['dog_birthday']
        if data.get('dog_weight'):
            dog_record['dog_weight'] = data['dog_weight']
        if data.get('dog_color'):
            dog_record['dog_color'] = data['dog_color']
        if data.get('shelter_entry_date'):
            dog_record['shelter_entry_date'] = data['shelter_entry_date']
        
        # Save to DynamoDB
        dogs_table.put_item(Item=dog_record)
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Dog registered successfully',
                'dog_id': dog_id,
                'shelter_id': shelter_id,
                'image_url': dog_record['image_url'],
                'created_at': dog_record['created_at']
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        logger.error(f"Error completing dog registration: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Failed to complete registration'})
        }

def generate_shelter_id(shelter: str, city: str, state: str) -> str:
    """Generate consistent shelter ID from location data"""
    return f"{state}#{city}#{shelter}".replace(' ', '_').upper()

def encrypt_dog_name(name: str) -> str:
    """Encrypt dog name using KMS for privacy"""
    try:
        response = kms_client.encrypt(
            KeyId=KMS_KEY_ID,
            Plaintext=name.encode('utf-8')
        )
        import base64
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encrypting dog name: {str(e)}")
        raise