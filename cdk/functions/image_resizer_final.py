import json
import boto3
import os
import logging
from urllib.parse import unquote_plus
from datetime import datetime, timezone
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
    Lambda function that resizes images using Pillow from Lambda layer
    """
    
    try:
        logger.info("=== IMAGE RESIZING STARTED ===")
        
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing: {object_key}")
            
            # Only process images in uploads/images/
            if not object_key.startswith('uploads/images/'):
                logger.info("Skipping - not in uploads/images/")
                continue
            
            # Download original image
            logger.info("Downloading original image...")
            original_data = download_image_from_s3(bucket_name, object_key)
            if not original_data:
                logger.error("Failed to download original image")
                continue
            
            logger.info(f"Original image size: {len(original_data)} bytes")
            
            # Generate keys for processed images
            base_name = object_key.replace('uploads/images/', '').split('.')[0]
            resized_key = f"processed/resized/{base_name}_400x400.jpg"
            thumbnail_key = f"processed/thumbnails/{base_name}_50x50.jpg"
            
            logger.info(f"Will create: {resized_key}")
            logger.info(f"Will create: {thumbnail_key}")
            
            # Create resized versions
            logger.info("Creating 400x400 version...")
            resized_data = resize_image(original_data, 400, 400)
            
            logger.info("Creating 50x50 version...")
            thumbnail_data = resize_image(original_data, 50, 50)
            
            if resized_data and thumbnail_data:
                logger.info(f"Resized image size: {len(resized_data)} bytes")
                logger.info(f"Thumbnail image size: {len(thumbnail_data)} bytes")
                
                # Upload resized images
                logger.info("Uploading 400x400 version...")
                success1 = upload_image_to_s3(bucket_name, resized_key, resized_data, 'image/jpeg')
                
                logger.info("Uploading 50x50 version...")
                success2 = upload_image_to_s3(bucket_name, thumbnail_key, thumbnail_data, 'image/jpeg')
                
                if success1 and success2:
                    logger.info("=== SUCCESS: Both images resized and uploaded ===")
                else:
                    logger.error("=== FAILED: Upload failed ===")
            else:
                logger.error("=== FAILED: Resizing failed ===")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image resizing completed'})
        }
        
    except Exception as e:
        logger.error(f"=== ERROR: {str(e)} ===")
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

def resize_image(image_data, target_width, target_height):
    """
    Resize image to exact dimensions using Pillow from Lambda layer
    """
    try:
        from PIL import Image
        
        logger.info(f"Resizing to {target_width}x{target_height}")
        
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        logger.info(f"Original size: {image.size}")
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            logger.info(f"Converting from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Resize to exact dimensions
        resized_image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized to: {resized_image.size}")
        
        # Save to bytes
        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, format='JPEG', quality=85, optimize=True)
        resized_data = output_buffer.getvalue()
        
        logger.info(f"Compressed size: {len(resized_data)} bytes")
        return resized_data
        
    except ImportError as e:
        logger.error(f"PIL not available: {str(e)}")
        return None
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
        logger.info(f"Successfully uploaded: {key}")
        return True
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return False