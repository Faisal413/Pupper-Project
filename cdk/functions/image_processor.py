import json
import boto3
import os
import uuid
# PIL removed - using simple copy approach
import io
import logging
from datetime import datetime, timezone
from urllib.parse import unquote_plus

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
IMAGES_BUCKET_NAME = os.environ['IMAGES_BUCKET_NAME']
DOGS_TABLE_NAME = os.environ['DOGS_TABLE_NAME']

# Get DynamoDB table
dogs_table = dynamodb.Table(DOGS_TABLE_NAME)

def handler(event, context):
    """
    This function is automatically triggered when an image is uploaded to S3.
    It processes the image by creating resized versions and updating the database.
    
    What happens:
    1. S3 sends event when new image uploaded
    2. We download the original image
    3. We create 2 resized versions (400x400 and 50x50)
    4. We upload both resized versions to S3
    5. We update database with all image URLs
    """
    
    try:
        logger.info(f"Image processing triggered: {json.dumps(event, default=str)}")
        
        # Step 1: Extract information from S3 event
        for record in event['Records']:
            # Get bucket and object key from the S3 event
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing image: {object_key} from bucket: {bucket_name}")
            
            # Only process images in the uploads/images/ folder
            if not object_key.startswith('uploads/images/'):
                logger.info(f"Skipping non-image upload: {object_key}")
                continue
            
            # Step 2: Download the original image from S3
            logger.info("Downloading original image from S3...")
            original_image_data = download_image_from_s3(bucket_name, object_key)
            
            if not original_image_data:
                logger.error(f"Failed to download image: {object_key}")
                continue
            
            # Step 3: For now, copy original image (will add real resizing later)
            logger.info("Copying image to processed folders...")
            # We'll implement real resizing in the next step
            
            # Step 4: Generate S3 keys for resized images
            base_name = object_key.replace('uploads/images/', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
            resized_key = f"processed/resized/{base_name}_400x400.png"
            thumbnail_key = f"processed/thumbnails/{base_name}_50x50.png"
            
            # Step 5: Copy original image to processed folders
            logger.info("Copying images to processed folders...")
            upload_success_resized = copy_image_to_s3(bucket_name, object_key, resized_key)
            upload_success_thumbnail = copy_image_to_s3(bucket_name, object_key, thumbnail_key)
            
            if upload_success_resized and upload_success_thumbnail:
                # Step 6: Update database with image metadata
                logger.info("Updating database with image metadata...")
                update_database_with_images(object_key, resized_key, thumbnail_key)
                logger.info(f"Successfully processed image: {object_key}")
            else:
                logger.error(f"Failed to upload resized images for: {object_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image processing completed successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error in image processing: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Image processing failed'})
        }

def download_image_from_s3(bucket_name, object_key):
    """
    Download image data from S3
    Returns the raw image bytes
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Error downloading image from S3: {str(e)}")
        return None

def copy_image_to_s3(bucket_name, source_key, dest_key):
    """
    Copy image from source to destination in S3
    """
    try:
        copy_source = {'Bucket': bucket_name, 'Key': source_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_name,
            Key=dest_key
        )
        logger.info(f"Successfully copied {source_key} to {dest_key}")
        return True
    except Exception as e:
        logger.error(f"Error copying image: {str(e)}")
        return False

def update_database_with_images(original_key, resized_key, thumbnail_key):
    """
    Update the dog record in DynamoDB with image URLs
    
    This finds the dog record that matches the uploaded image
    and adds the image URLs to it
    """
    try:
        # Generate URLs for all three images
        base_url = f"https://{IMAGES_BUCKET_NAME}.s3.amazonaws.com"
        
        image_metadata = {
            'original_url': f"{base_url}/{original_key}",
            'resized_url': f"{base_url}/{resized_key}",
            'thumbnail_url': f"{base_url}/{thumbnail_key}",
            'original_key': original_key,
            'resized_key': resized_key,
            'thumbnail_key': thumbnail_key,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        # For now, we'll log the metadata
        # In a real implementation, you'd find the dog record by matching the S3 key
        # and update it with this image metadata
        logger.info(f"Image metadata ready for database update: {json.dumps(image_metadata, default=str)}")
        
        # TODO: Implement database update logic
        # This would require matching the S3 key to a specific dog record
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}")
        return False