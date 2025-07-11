import json
import boto3
import os
import logging
from urllib.parse import unquote_plus
import io
from PIL import Image, ImageOps

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
    High-quality image resizer that preserves image quality while changing dimensions
    """
    
    try:
        logger.info("=== HIGH-QUALITY RESIZING STARTED ===")
        
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing: {object_key}")
            
            if not object_key.startswith('uploads/images/'):
                continue
            
            # Download original image
            original_data = download_image_from_s3(bucket_name, object_key)
            if not original_data:
                continue
            
            # Get original image info
            original_image = Image.open(io.BytesIO(original_data))
            logger.info(f"Original: {original_image.size} - Mode: {original_image.mode}")
            
            # Generate keys
            base_name = object_key.replace('uploads/images/', '').split('.')[0]
            resized_key = f"processed/resized/{base_name}_400x400.png"
            thumbnail_key = f"processed/thumbnails/{base_name}_50x50.png"
            
            # Create high-quality resized versions
            logger.info("Creating 400x400 version (high quality)...")
            resized_data = resize_image_high_quality(original_data, 400, 400)
            
            logger.info("Creating 50x50 version (high quality)...")
            thumbnail_data = resize_image_high_quality(original_data, 50, 50)
            
            if resized_data and thumbnail_data:
                # Upload as PNG to preserve quality
                logger.info("Uploading high-quality resized images...")
                upload_image_to_s3(bucket_name, resized_key, resized_data, 'image/png')
                upload_image_to_s3(bucket_name, thumbnail_key, thumbnail_data, 'image/png')
                
                # Verify final dimensions
                verify_final_dimensions(resized_data, "400x400")
                verify_final_dimensions(thumbnail_data, "50x50")
                
                logger.info("=== SUCCESS: High-quality resizing completed ===")
            else:
                logger.error("=== FAILED: High-quality resizing failed ===")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'High-quality resizing completed'})
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

def resize_image_high_quality(image_data, target_width, target_height):
    """
    Resize image with maximum quality preservation
    Uses Lanczos resampling for best quality
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        logger.info(f"Input: {image.size}, Mode: {image.mode}")
        
        # Convert to RGB if needed (for consistent processing)
        if image.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        elif image.mode == 'P':
            image = image.convert('RGB')
        elif image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Apply auto-orientation if needed
        image = ImageOps.exif_transpose(image)
        
        # Resize using highest quality method
        # Lanczos is the best quality resampling filter
        resized_image = image.resize(
            (target_width, target_height), 
            Image.Resampling.LANCZOS
        )
        
        logger.info(f"Resized to: {resized_image.size}")
        
        # Save as PNG with maximum quality (no compression loss)
        output_buffer = io.BytesIO()
        resized_image.save(
            output_buffer, 
            format='PNG',
            optimize=False,  # No optimization to preserve quality
            compress_level=0  # No compression
        )
        
        result_data = output_buffer.getvalue()
        logger.info(f"Output size: {len(result_data)} bytes")
        
        return result_data
        
    except Exception as e:
        logger.error(f"High-quality resize error: {str(e)}")
        return None

def verify_final_dimensions(image_data, expected_size):
    """Verify the final dimensions"""
    try:
        image = Image.open(io.BytesIO(image_data))
        logger.info(f"VERIFIED {expected_size}: Actual dimensions = {image.size}")
        return image.size
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
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