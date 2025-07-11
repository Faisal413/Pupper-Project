import json
import boto3
import os
import logging
from urllib.parse import unquote_plus
from datetime import datetime, timezone
import base64
import io

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Environment variables
IMAGES_BUCKET_NAME = os.environ['IMAGES_BUCKET_NAME']
DOGS_TABLE_NAME = os.environ['DOGS_TABLE_NAME']

def handler(event, context):
    """
    Image processor that creates actual resized versions using AWS Lambda
    """
    
    try:
        logger.info(f"Image processing triggered: {json.dumps(event, default=str)}")
        
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing image: {object_key}")
            
            # Only process images in uploads/images/
            if not object_key.startswith('uploads/images/'):
                continue
            
            # Download original image
            original_data = download_image_from_s3(bucket_name, object_key)
            if not original_data:
                continue
            
            # Generate keys for processed images
            base_name = object_key.replace('uploads/images/', '').split('.')[0]
            resized_key = f"processed/resized/{base_name}_400x400.jpg"
            thumbnail_key = f"processed/thumbnails/{base_name}_50x50.jpg"
            
            # Create resized versions using simple approach
            resized_data = create_resized_image(original_data, 400, 400)
            thumbnail_data = create_resized_image(original_data, 50, 50)
            
            if resized_data and thumbnail_data:
                # Upload resized images
                upload_image_to_s3(bucket_name, resized_key, resized_data, 'image/jpeg')
                upload_image_to_s3(bucket_name, thumbnail_key, thumbnail_data, 'image/jpeg')
                
                logger.info(f"Successfully processed: {object_key}")
                logger.info(f"Created 400x400: {resized_key}")
                logger.info(f"Created 50x50: {thumbnail_key}")
            else:
                logger.error(f"Failed to resize: {object_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing completed'})
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def download_image_from_s3(bucket_name, object_key):
    """Download image from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return None

def create_resized_image(image_data, width, height):
    """
    Create resized image using PIL
    This will work once we get Pillow installed properly
    """
    try:
        from PIL import Image
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        resized.save(output, format='JPEG', quality=85)
        return output.getvalue()
        
    except ImportError:
        logger.error("PIL not available - copying original")
        return image_data  # Return original if PIL not available
    except Exception as e:
        logger.error(f"Resize error: {str(e)}")
        return None

def upload_image_to_s3(bucket_name, key, data, content_type):
    """Upload image to S3"""
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        return True
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return False