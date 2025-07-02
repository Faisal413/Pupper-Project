import os
import json
import boto3
import uuid
import logging
import base64
from io import BytesIO
from datetime import datetime
from urllib.parse import unquote_plus
from PIL import Image

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
dogs_table = dynamodb.Table(os.environ['DOGS_TABLE_NAME'])
bucket_name = os.environ['IMAGES_BUCKET_NAME']

# Image sizes
STANDARD_SIZE = (400, 400)
THUMBNAIL_SIZE = (50, 50)

def resize_image(image_data, size):
    """Resize image to specified dimensions"""
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Convert to RGB if image has alpha channel (RGBA)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Resize image while maintaining aspect ratio
            img.thumbnail(size)
            
            # Save to BytesIO object
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise

def process_image(bucket, key, dog_id, shelter_id):
    """Process uploaded image: create standard and thumbnail versions"""
    try:
        # Get the uploaded image
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        content_type = response.get('ContentType', 'image/jpeg')
        
        # Generate unique IDs for processed images
        image_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Extract original filename from key
        filename = key.split('/')[-1]
        base_filename, ext = os.path.splitext(filename)
        
        # Create paths for processed images
        original_key = f"dogs/{dog_id}/original/{image_id}{ext}"
        standard_key = f"dogs/{dog_id}/standard/{image_id}.png"
        thumbnail_key = f"dogs/{dog_id}/thumbnail/{image_id}.png"
        
        # Store original image
        s3_client.put_object(
            Bucket=bucket,
            Key=original_key,
            Body=image_data,
            ContentType=content_type
        )
        
        # Create and store standard size image
        standard_image = resize_image(image_data, STANDARD_SIZE)
        s3_client.put_object(
            Bucket=bucket,
            Key=standard_key,
            Body=standard_image,
            ContentType='image/png'
        )
        
        # Create and store thumbnail
        thumbnail_image = resize_image(image_data, THUMBNAIL_SIZE)
        s3_client.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=thumbnail_image,
            ContentType='image/png'
        )
        
        # Update DynamoDB with image metadata
        image_metadata = {
            'image_id': image_id,
            'original_key': original_key,
            'standard_key': standard_key,
            'thumbnail_key': thumbnail_key,
            'content_type': content_type,
            'created_at': timestamp,
            'original_filename': filename
        }
        
        # Update the dog record with the new image
        dogs_table.update_item(
            Key={
                'shelter_id': shelter_id,
                'dog_id': dog_id
            },
            UpdateExpression="SET images = list_append(if_not_exists(images, :empty_list), :image)",
            ExpressionAttributeValues={
                ':image': [image_metadata],
                ':empty_list': []
            }
        )
        
        # Delete the original upload now that we've processed it
        s3_client.delete_object(Bucket=bucket, Key=key)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image processed successfully',
                'image_id': image_id,
                'dog_id': dog_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error processing image: {str(e)}'
            })
        }

def handler(event, context):
    """Lambda handler for processing uploaded images"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle S3 event trigger
        if 'Records' in event and event['Records'][0].get('eventSource') == 'aws:s3':
            record = event['Records'][0]
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            # Extract dog_id and shelter_id from the key
            # Expected format: uploads/{shelter_id}/{dog_id}/{filename}
            path_parts = key.split('/')
            if len(path_parts) >= 4 and path_parts[0] == 'uploads':
                shelter_id = path_parts[1]
                dog_id = path_parts[2]
                return process_image(bucket, key, dog_id, shelter_id)
            else:
                logger.error(f"Invalid key format: {key}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Invalid key format: {key}. Expected: uploads/{{shelter_id}}/{{dog_id}}/{{filename}}'
                    })
                }
        
        # Handle direct Lambda invocation (for testing)
        elif 'dog_id' in event and 'shelter_id' in event and 'key' in event:
            return process_image(
                event.get('bucket', bucket_name),
                event['key'],
                event['dog_id'],
                event['shelter_id']
            )
        
        else:
            logger.error("Invalid event structure")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid event structure'
                })
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error in handler: {str(e)}'
            })
        }
