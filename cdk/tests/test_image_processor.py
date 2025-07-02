import os
import json
import pytest
import boto3
import base64
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
import sys

# Add the functions directory to the path so we can import the module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
import image_processor

@pytest.fixture
def mock_env():
    """Set up mock environment variables"""
    with patch.dict(os.environ, {
        'DOGS_TABLE_NAME': 'test-dogs-table',
        'IMAGES_BUCKET_NAME': 'test-images-bucket'
    }):
        yield

@pytest.fixture
def mock_s3():
    """Mock S3 client"""
    with patch('boto3.client') as mock_client:
        s3_mock = MagicMock()
        mock_client.return_value = s3_mock
        yield s3_mock

@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB resource and table"""
    with patch('boto3.resource') as mock_resource:
        dynamodb_mock = MagicMock()
        table_mock = MagicMock()
        dynamodb_mock.Table.return_value = table_mock
        mock_resource.return_value = dynamodb_mock
        yield table_mock

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

def test_resize_image(sample_image):
    """Test image resizing functionality"""
    # Test standard size
    standard_size = (400, 400)
    resized = image_processor.resize_image(sample_image, standard_size)
    
    # Load the resized image to verify dimensions
    with Image.open(BytesIO(resized)) as img:
        # The image should be smaller or equal to the target size
        assert img.width <= standard_size[0]
        assert img.height <= standard_size[1]
    
    # Test thumbnail size
    thumbnail_size = (50, 50)
    resized = image_processor.resize_image(sample_image, thumbnail_size)
    
    # Load the resized image to verify dimensions
    with Image.open(BytesIO(resized)) as img:
        # The image should be smaller or equal to the target size
        assert img.width <= thumbnail_size[0]
        assert img.height <= thumbnail_size[1]

def test_process_image(mock_env, mock_s3, mock_dynamodb, sample_image):
    """Test the image processing workflow"""
    # Mock S3 get_object response
    mock_s3.get_object.return_value = {
        'Body': MagicMock(read=lambda: sample_image),
        'ContentType': 'image/png'
    }
    
    # Call the process_image function
    result = image_processor.process_image(
        bucket='test-bucket',
        key='uploads/test-shelter-id/test-dog-id/test.png',
        dog_id='test-dog-id',
        shelter_id='test-shelter-id'
    )
    
    # Verify S3 operations
    assert mock_s3.get_object.called
    assert mock_s3.put_object.call_count == 3  # Original, standard, thumbnail
    
    # Verify DynamoDB update
    assert mock_dynamodb.update_item.called
    
    # Verify the result
    assert result['statusCode'] == 200
    assert 'image processed successfully' in result['body'].lower()

def test_handler_s3_event(mock_env, mock_s3, mock_dynamodb):
    """Test the Lambda handler with an S3 event"""
    # Create a mock S3 event
    event = {
        'Records': [{
            'eventSource': 'aws:s3',
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'uploads/test-shelter-id/test-dog-id/test.png'}
            }
        }]
    }
    
    # Mock the process_image function
    with patch('image_processor.process_image') as mock_process:
        mock_process.return_value = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image processed successfully'})
        }
        
        # Call the handler
        result = image_processor.handler(event, None)
        
        # Verify process_image was called with correct parameters
        mock_process.assert_called_with(
            'test-bucket',
            'uploads/test-shelter-id/test-dog-id/test.png',
            'test-dog-id',
            'test-shelter-id'
        )
        
        # Verify the result
        assert result['statusCode'] == 200

def test_handler_direct_invocation(mock_env, mock_s3, mock_dynamodb):
    """Test the Lambda handler with direct invocation"""
    # Create a direct invocation event
    event = {
        'bucket': 'test-bucket',
        'key': 'uploads/test-shelter-id/test-dog-id/test.png',
        'dog_id': 'test-dog-id',
        'shelter_id': 'test-shelter-id'
    }
    
    # Mock the process_image function
    with patch('image_processor.process_image') as mock_process:
        mock_process.return_value = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image processed successfully'})
        }
        
        # Call the handler
        result = image_processor.handler(event, None)
        
        # Verify process_image was called with correct parameters
        mock_process.assert_called_with(
            'test-bucket',
            'uploads/test-shelter-id/test-dog-id/test.png',
            'test-dog-id',
            'test-shelter-id'
        )
        
        # Verify the result
        assert result['statusCode'] == 200

def test_handler_invalid_event(mock_env):
    """Test the Lambda handler with an invalid event"""
    # Create an invalid event
    event = {'invalid': 'event'}
    
    # Call the handler
    result = image_processor.handler(event, None)
    
    # Verify the result
    assert result['statusCode'] == 400
    assert 'invalid event structure' in result['body'].lower()
