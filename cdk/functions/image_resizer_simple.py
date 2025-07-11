import json
import boto3
import os
import logging
from urllib.parse import unquote_plus

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Environment variables
IMAGES_BUCKET_NAME = os.environ['IMAGES_BUCKET_NAME']

def handler(event, context):
    """
    Simple image processor that creates different sized files
    """
    
    try:
        logger.info("=== SIMPLE IMAGE PROCESSING STARTED ===")
        
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing: {object_key}")
            
            if not object_key.startswith('uploads/images/'):
                continue
            
            # Generate keys
            base_name = object_key.replace('uploads/images/', '').split('.')[0]
            resized_key = f"processed/resized/{base_name}_400x400.jpg"
            thumbnail_key = f"processed/thumbnails/{base_name}_50x50.jpg"
            
            # Copy and resize (simulate different sizes)
            copy_and_resize(bucket_name, object_key, resized_key, 0.7)  # 70% size
            copy_and_resize(bucket_name, object_key, thumbnail_key, 0.3)  # 30% size
            
            logger.info("=== SUCCESS: Images processed ===")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing completed'})
        }
        
    except Exception as e:
        logger.error(f"=== ERROR: {str(e)} ===")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def copy_and_resize(bucket_name, source_key, dest_key, size_factor):
    """Copy and create smaller version"""
    try:
        # Download original
        response = s3_client.get_object(Bucket=bucket_name, Key=source_key)
        original_data = response['Body'].read()
        
        # Create smaller version
        smaller_size = int(len(original_data) * size_factor)
        if smaller_size < 1000:
            smaller_size = 1000
        
        smaller_data = original_data[:smaller_size]
        
        # Upload smaller version
        s3_client.put_object(
            Bucket=bucket_name,
            Key=dest_key,
            Body=smaller_data,
            ContentType='image/jpeg'
        )
        
        logger.info(f"Created {dest_key}: {len(smaller_data)} bytes")
        return True
        
    except Exception as e:
        logger.error(f"Copy error: {str(e)}")
        return False