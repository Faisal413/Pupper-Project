import json
import boto3
import os
import uuid
import logging
import base64
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional
import re

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
kms = boto3.client('kms')
s3 = boto3.client('s3')

# Environment variables
DOGS_TABLE_NAME = os.environ['DOGS_TABLE_NAME']
INTERACTIONS_TABLE_NAME = os.environ['INTERACTIONS_TABLE_NAME']
KMS_KEY_ID = os.environ['KMS_KEY_ID']
IMAGES_BUCKET_NAME = os.environ['IMAGES_BUCKET_NAME']

dogs_table = dynamodb.Table(DOGS_TABLE_NAME)
interactions_table = dynamodb.Table(INTERACTIONS_TABLE_NAME)

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL for S3 object"""
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name,
                                                    'Key': object_name},
                                             ExpiresIn=expiration)
        return response
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None

def handle_image_upload(dog_id, shelter_id, request_body, request_id):
    """Handle image upload for a dog"""
    try:
        # Check if the request contains base64 encoded image data
        if 'image_data' not in request_body or 'filename' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing required fields: image_data and filename'
                })
            }
        
        # Extract image data and decode from base64
        image_data = request_body['image_data']
        
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]
            
        try:
            decoded_image = base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Error decoding base64 image: {str(e)}", extra={"request_id": request_id})
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid base64 encoded image data'
                })
            }
        
        # Generate a unique filename
        filename = request_body['filename']
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Validate file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if file_extension not in valid_extensions:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f'Invalid file extension. Allowed: {", ".join(valid_extensions)}'
                })
            }
        
        # Create a unique key for the uploaded image
        upload_key = f"uploads/{shelter_id}/{dog_id}/{str(uuid.uuid4())}{file_extension}"
        
        # Upload the image to S3
        s3.put_object(
            Bucket=IMAGES_BUCKET_NAME,
            Key=upload_key,
            Body=decoded_image,
            ContentType=f"image/{file_extension[1:]}"  # Remove the dot from extension
        )
        
        return {
            'statusCode': 202,  # Accepted - processing will happen asynchronously
            'body': json.dumps({
                'message': 'Image uploaded successfully and is being processed',
                'upload_key': upload_key
            })
        }
        
    except Exception as e:
        logger.error(f"Error handling image upload: {str(e)}", extra={"request_id": request_id})
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error handling image upload: {str(e)}'
            })
        }

def get_dog_images(dog_id, shelter_id, request_id):
    """Get all images for a specific dog"""
    try:
        # Get the dog record
        response = dogs_table.get_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Dog not found with ID: {dog_id}'
                })
            }
        
        dog = response['Item']
        
        # Check if the dog has images
        if 'images' not in dog or not dog['images']:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No images found for this dog',
                    'images': []
                })
            }
        
        # Generate presigned URLs for each image
        images_with_urls = []
        for image in dog['images']:
            image_with_urls = image.copy()
            
            # Generate URLs with 1 hour expiration
            image_with_urls['original_url'] = generate_presigned_url(
                IMAGES_BUCKET_NAME, image['original_key'], 3600)
            image_with_urls['standard_url'] = generate_presigned_url(
                IMAGES_BUCKET_NAME, image['standard_key'], 3600)
            image_with_urls['thumbnail_url'] = generate_presigned_url(
                IMAGES_BUCKET_NAME, image['thumbnail_key'], 3600)
                
            images_with_urls.append(image_with_urls)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'dog_id': dog_id,
                'shelter_id': shelter_id,
                'images': images_with_urls
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting dog images: {str(e)}", extra={"request_id": request_id})
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error getting dog images: {str(e)}'
            })
        }

def get_specific_image(dog_id, shelter_id, image_id, request_id):
    """Get a specific image for a dog"""
    try:
        # Get the dog record
        response = dogs_table.get_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Dog not found with ID: {dog_id}'
                })
            }
        
        dog = response['Item']
        
        # Check if the dog has images
        if 'images' not in dog or not dog['images']:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'No images found for dog with ID: {dog_id}'
                })
            }
        
        # Find the specific image
        image = next((img for img in dog['images'] if img['image_id'] == image_id), None)
        
        if not image:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Image not found with ID: {image_id}'
                })
            }
        
        # Generate presigned URLs
        image_with_urls = image.copy()
        image_with_urls['original_url'] = generate_presigned_url(
            IMAGES_BUCKET_NAME, image['original_key'], 3600)
        image_with_urls['standard_url'] = generate_presigned_url(
            IMAGES_BUCKET_NAME, image['standard_key'], 3600)
        image_with_urls['thumbnail_url'] = generate_presigned_url(
            IMAGES_BUCKET_NAME, image['thumbnail_key'], 3600)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'dog_id': dog_id,
                'shelter_id': shelter_id,
                'image': image_with_urls
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting specific image: {str(e)}", extra={"request_id": request_id})
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error getting specific image: {str(e)}'
            })
        }

def delete_image(dog_id, shelter_id, image_id, request_id):
    """Delete a specific image for a dog"""
    try:
        # Get the dog record
        response = dogs_table.get_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Dog not found with ID: {dog_id}'
                })
            }
        
        dog = response['Item']
        
        # Check if the dog has images
        if 'images' not in dog or not dog['images']:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'No images found for dog with ID: {dog_id}'
                })
            }
        
        # Find the specific image
        image = next((img for img in dog['images'] if img['image_id'] == image_id), None)
        
        if not image:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Image not found with ID: {image_id}'
                })
            }
        
        # Delete the image files from S3
        s3.delete_object(Bucket=IMAGES_BUCKET_NAME, Key=image['original_key'])
        s3.delete_object(Bucket=IMAGES_BUCKET_NAME, Key=image['standard_key'])
        s3.delete_object(Bucket=IMAGES_BUCKET_NAME, Key=image['thumbnail_key'])
        
        # Remove the image from the dog's record
        updated_images = [img for img in dog['images'] if img['image_id'] != image_id]
        
        dogs_table.update_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            },
            UpdateExpression="SET images = :images",
            ExpressionAttributeValues={
                ':images': updated_images
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Image {image_id} deleted successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}", extra={"request_id": request_id})
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error deleting image: {str(e)}'
            })
        }

def handler(event, context):
    """
    Main Lambda handler for dog-related operations
    """
    request_id = context.aws_request_id if context else str(uuid.uuid4())
    
    # Structured logging
    headers = event.get('headers') or {}
    logger.info("Request started", extra={
        "request_id": request_id,
        "http_method": event.get('httpMethod'),
        "path": event.get('path'),
        "user_agent": headers.get('User-Agent', 'Unknown')
    })
    
    try:
        http_method = event['httpMethod']
        path = event['path']
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        # Parse request body if present
        request_body = {}
        if body:
            try:
                request_body = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON in request body", extra={
                    "request_id": request_id,
                    "error": str(e),
                    "body": body[:100]  # Log first 100 chars for debugging
                })
                return create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Route requests based on path and method
        if path == '/dogs':
            if http_method == 'GET':
                return get_dogs(query_parameters, request_id)
            elif http_method == 'POST':
                return create_dog(request_body, request_id)
        
        elif path.startswith('/dogs/') and 'dog_id' in path_parameters:
            dog_id = path_parameters['dog_id']
            
            # Check if this is an image-related request
            if '/images' in path:
                shelter_id = query_parameters.get('shelter_id')
                if not shelter_id:
                    return create_response(400, {'error': 'Missing required query parameter: shelter_id'})
                
                # Handle image endpoints
                if path.endswith('/images'):
                    if http_method == 'GET':
                        return get_dog_images(dog_id, shelter_id, request_id)
                    elif http_method == 'POST':
                        return handle_image_upload(dog_id, shelter_id, request_body, request_id)
                elif 'image_id' in path_parameters:
                    image_id = path_parameters['image_id']
                    if http_method == 'GET':
                        return get_specific_image(dog_id, shelter_id, image_id, request_id)
                    elif http_method == 'DELETE':
                        return delete_image(dog_id, shelter_id, image_id, request_id)
            else:
                # Regular dog endpoints
                if http_method == 'GET':
                    return get_dog(dog_id, query_parameters, request_id)
                elif http_method == 'PUT':
                    return update_dog(dog_id, request_body, request_id)
                elif http_method == 'DELETE':
                    return delete_dog(dog_id, query_parameters, request_id)
        
        elif path == '/interactions':
            if http_method == 'POST':
                return create_interaction(request_body, request_id)
            elif http_method == 'GET':
                return get_user_interactions(query_parameters, request_id)
        
        elif path == '/upload':
            if http_method == 'POST':
                return handle_simple_upload(request_body, request_id)
        
        logger.warning("Endpoint not found", extra={
            "request_id": request_id,
            "path": path,
            "method": http_method
        })
        return create_response(404, {'error': 'Endpoint not found'})
        
    except Exception as e:
        logger.error("Unhandled exception", extra={
            "request_id": request_id,
            "error": str(e),
            "error_type": type(e).__name__
        })
        return create_response(500, {'error': 'Internal server error'})

def create_dog(dog_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new dog entry"""
    try:
        # Validate required fields
        required_fields = ['shelter', 'city', 'state', 'dog_name', 'species', 'description']
        for field in required_fields:
            if field not in dog_data:
                return create_response(400, {'error': f'Missing required field: {field}'})
        
        # Validate that it's a Labrador Retriever
        species = dog_data.get('species', '').lower()
        if 'labrador' not in species and 'lab' not in species:
            return create_response(400, {'error': 'Only Labrador Retrievers are accepted'})
        
        # Generate IDs
        shelter_id = generate_shelter_id(dog_data['shelter'], dog_data['city'], dog_data['state'])
        dog_id = str(uuid.uuid4())
        
        # Encrypt dog name
        encrypted_name = encrypt_dog_name(dog_data['dog_name'])
        
        # Prepare dog item
        dog_item = {
            'shelter_id': shelter_id,
            'dog_id': dog_id,
            'shelter': dog_data['shelter'],
            'city': dog_data['city'],
            'state': dog_data['state'],
            'encrypted_dog_name': encrypted_name,
            'species': dog_data['species'],
            'description': dog_data['description'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Optional fields with validation
        if 'shelter_entry_date' in dog_data:
            dog_item['shelter_entry_date'] = dog_data['shelter_entry_date']
        
        if 'dog_birthday' in dog_data:
            dog_item['dog_birthday'] = dog_data['dog_birthday']
        
        if 'dog_weight' in dog_data:
            try:
                # Handle weight conversion from string to number
                weight = parse_weight(dog_data['dog_weight'])
                if weight:
                    dog_item['dog_weight'] = Decimal(str(weight))
            except (ValueError, TypeError):
                print(f"Invalid weight format: {dog_data['dog_weight']}")
        
        if 'dog_color' in dog_data:
            dog_item['dog_color'] = dog_data['dog_color']
        
        # Store in DynamoDB
        dogs_table.put_item(Item=dog_item)
        
        # Return response without encrypted name
        response_item = dog_item.copy()
        response_item['dog_name'] = dog_data['dog_name']  # Return original name
        del response_item['encrypted_dog_name']
        
        return create_response(201, {
            'message': 'Dog created successfully',
            'dog': response_item
        })
        
    except Exception as e:
        print(f'Error creating dog: {str(e)}')
        return create_response(500, {'error': 'Failed to create dog'})

def get_dogs(query_params: Dict[str, str]) -> Dict[str, Any]:
    """Get dogs with optional filtering"""
    try:
        # Start with scanning the table (can be optimized with GSI queries)
        scan_kwargs = {}
        filter_expressions = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        # Filter by state using GSI
        if 'state' in query_params:
            response = dogs_table.query(
                IndexName='StateIndex',
                KeyConditionExpression='#state = :state',
                ExpressionAttributeNames={'#state': 'state'},
                ExpressionAttributeValues={':state': query_params['state']}
            )
            items = response['Items']
        else:
            # Scan all items if no state filter
            response = dogs_table.scan()
            items = response['Items']
        
        # Apply additional filters
        filtered_items = []
        for item in items:
            # Filter by species (ensure only Labrador Retrievers)
            species = item.get('species', '').lower()
            if 'labrador' not in species and 'lab' not in species:
                continue
            
            # Filter by weight range
            if 'min_weight' in query_params or 'max_weight' in query_params:
                weight = item.get('dog_weight')
                if weight:
                    weight = float(weight)
                    if 'min_weight' in query_params and weight < float(query_params['min_weight']):
                        continue
                    if 'max_weight' in query_params and weight > float(query_params['max_weight']):
                        continue
            
            # Filter by color
            if 'color' in query_params:
                dog_color = item.get('dog_color', '').lower()
                if query_params['color'].lower() not in dog_color:
                    continue
            
            # Decrypt dog name for response
            if 'encrypted_dog_name' in item:
                try:
                    item['dog_name'] = decrypt_dog_name(item['encrypted_dog_name'])
                    del item['encrypted_dog_name']
                except Exception as e:
                    print(f"Error decrypting dog name: {str(e)}")
                    item['dog_name'] = "Name unavailable"
            
            filtered_items.append(item)
        
        return create_response(200, {
            'dogs': filtered_items,
            'count': len(filtered_items)
        })
        
    except Exception as e:
        print(f'Error getting dogs: {str(e)}')
        return create_response(500, {'error': 'Failed to retrieve dogs'})

def get_dog(dog_id: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    """Get a specific dog by ID"""
    try:
        # Need shelter_id to get the dog
        shelter_id = query_params.get('shelter_id')
        if not shelter_id:
            return create_response(400, {'error': 'shelter_id query parameter is required'})
        
        response = dogs_table.get_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            }
        )
        
        if 'Item' not in response:
            return create_response(404, {'error': 'Dog not found'})
        
        item = response['Item']
        
        # Decrypt dog name
        if 'encrypted_dog_name' in item:
            try:
                item['dog_name'] = decrypt_dog_name(item['encrypted_dog_name'])
                del item['encrypted_dog_name']
            except Exception as e:
                print(f"Error decrypting dog name: {str(e)}")
                item['dog_name'] = "Name unavailable"
        
        return create_response(200, {'dog': item})
        
    except Exception as e:
        print(f'Error getting dog: {str(e)}')
        return create_response(500, {'error': 'Failed to retrieve dog'})

def create_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a user interaction (wag/growl)"""
    try:
        required_fields = ['user_id', 'shelter_id', 'dog_id', 'interaction_type']
        for field in required_fields:
            if field not in interaction_data:
                return create_response(400, {'error': f'Missing required field: {field}'})
        
        if interaction_data['interaction_type'] not in ['wag', 'growl']:
            return create_response(400, {'error': 'interaction_type must be "wag" or "growl"'})
        
        dog_key = f"{interaction_data['shelter_id']}#{interaction_data['dog_id']}"
        
        interaction_item = {
            'user_id': interaction_data['user_id'],
            'dog_key': dog_key,
            'shelter_id': interaction_data['shelter_id'],
            'dog_id': interaction_data['dog_id'],
            'interaction_type': interaction_data['interaction_type'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        interactions_table.put_item(Item=interaction_item)
        
        return create_response(201, {
            'message': 'Interaction recorded successfully',
            'interaction': interaction_item
        })
        
    except Exception as e:
        print(f'Error creating interaction: {str(e)}')
        return create_response(500, {'error': 'Failed to record interaction'})

def get_user_interactions(query_params: Dict[str, str]) -> Dict[str, Any]:
    """Get user's interactions"""
    try:
        user_id = query_params.get('user_id')
        if not user_id:
            return create_response(400, {'error': 'user_id query parameter is required'})
        
        response = interactions_table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        return create_response(200, {
            'interactions': response['Items'],
            'count': len(response['Items'])
        })
        
    except Exception as e:
        print(f'Error getting user interactions: {str(e)}')
        return create_response(500, {'error': 'Failed to retrieve interactions'})

# Helper functions
def generate_shelter_id(shelter: str, city: str, state: str) -> str:
    """Generate a consistent shelter ID"""
    return f"{state}#{city}#{shelter}".replace(' ', '_').upper()

def encrypt_dog_name(name: str) -> str:
    """Encrypt dog name using KMS"""
    try:
        response = kms.encrypt(
            KeyId=KMS_KEY_ID,
            Plaintext=name.encode('utf-8')
        )
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
    except Exception as e:
        print(f"Error encrypting dog name: {str(e)}")
        raise

def decrypt_dog_name(encrypted_name: str) -> str:
    """Decrypt dog name using KMS"""
    try:
        ciphertext_blob = base64.b64decode(encrypted_name.encode('utf-8'))
        response = kms.decrypt(CiphertextBlob=ciphertext_blob)
        return response['Plaintext'].decode('utf-8')
    except Exception as e:
        print(f"Error decrypting dog name: {str(e)}")
        raise

def parse_weight(weight_str) -> Optional[float]:
    """Parse weight from various string formats"""
    if isinstance(weight_str, (int, float)):
        return float(weight_str)
    
    if isinstance(weight_str, str):
        # Remove common words and extract numbers
        import re
        numbers = re.findall(r'\d+\.?\d*', weight_str.lower())
        if numbers:
            return float(numbers[0])
    
    return None

def handle_simple_upload(request_body, request_id):
    """Generate presigned URL for S3 upload"""
    try:
        if 'filename' not in request_body:
            return create_response(400, {'error': 'Missing filename'})
        
        filename = request_body['filename']
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
            return create_response(400, {'error': 'Invalid file type'})
        
        upload_key = f"uploads/{str(uuid.uuid4())}{file_extension}"
        
        presigned_post = s3.generate_presigned_post(
            Bucket=IMAGES_BUCKET_NAME,
            Key=upload_key,
            ExpiresIn=3600
        )
        
        return create_response(200, {
            'upload_url': presigned_post['url'],
            'fields': presigned_post['fields'],
            'key': upload_key,
            'instructions': 'Use POST method with form-data. Add all fields, then add file as "file" field'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", extra={"request_id": request_id})
        return create_response(500, {'error': 'Failed to generate upload URL'})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }
