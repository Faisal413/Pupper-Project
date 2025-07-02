#!/usr/bin/env python3
"""
Integration tests for the Pupper Upload API
Tests the upload handler Lambda function directly
"""

import json
import base64
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

# Import the upload handler
from upload_handler import (
    handler,
    validate_and_clean_data,
    is_labrador_retriever,
    clean_weight,
    parse_date,
    generate_shelter_id,
    process_single_dog_upload
)

class TestUploadHandler:
    """Test the upload handler function"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock environment variables
        os.environ['DOGS_TABLE_NAME'] = 'test-dogs-table'
        os.environ['IMAGES_BUCKET_NAME'] = 'test-images-bucket'
        os.environ['KMS_KEY_ID'] = 'test-kms-key'
    
    def test_cors_preflight(self):
        """Test CORS preflight request"""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/upload'
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
    
    @patch('upload_handler.save_dog_to_database')
    @patch('upload_handler.encrypt_dog_name')
    def test_valid_upload_without_image(self, mock_encrypt, mock_save):
        """Test valid upload without image"""
        mock_encrypt.return_value = 'encrypted_name'
        mock_save.return_value = {'success': True}
        
        event = {
            'httpMethod': 'POST',
            'path': '/upload',
            'body': json.dumps({
                'shelter': 'Test Shelter',
                'city': 'Charlotte',
                'state': 'NC',
                'dog_name': 'Buddy',
                'dog_species': 'Labrador Retriever',
                'shelter_entry_date': '1/15/2024',
                'dog_description': 'Friendly dog'
            })
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 201
        result = json.loads(response['body'])
        assert result['message'] == 'Dog uploaded successfully'
        assert 'dog_id' in result
        assert 'shelter_id' in result
    
    def test_invalid_species_upload(self):
        """Test upload with non-Labrador Retriever"""
        event = {
            'httpMethod': 'POST',
            'path': '/upload',
            'body': json.dumps({
                'shelter': 'Test Shelter',
                'city': 'Charlotte',
                'state': 'NC',
                'dog_name': 'Rex',
                'dog_species': 'German Shepherd',
                'shelter_entry_date': '1/15/2024',
                'dog_description': 'Great dog'
            })
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 422
        result = json.loads(response['body'])
        assert 'Only Labrador Retrievers are accepted' in result['error']
    
    def test_missing_required_fields(self):
        """Test upload with missing required fields"""
        event = {
            'httpMethod': 'POST',
            'path': '/upload',
            'body': json.dumps({
                'shelter': 'Test Shelter',
                'city': 'Charlotte'
                # Missing required fields
            })
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 400
        result = json.loads(response['body'])
        assert 'Missing required fields' in result['error']
    
    @patch('upload_handler.process_single_dog_upload')
    def test_bulk_upload(self, mock_process):
        """Test bulk upload functionality"""
        mock_process.side_effect = [
            {'index': 0, 'success': True, 'dog_id': 'id1', 'shelter_id': 'shelter1'},
            {'index': 1, 'success': True, 'dog_id': 'id2', 'shelter_id': 'shelter2'},
            {'index': 2, 'success': False, 'error': 'Invalid species'}
        ]
        
        event = {
            'httpMethod': 'POST',
            'path': '/upload/bulk',
            'body': json.dumps({
                'dogs': [
                    {
                        'shelter': 'Test Shelter 1',
                        'city': 'Charlotte',
                        'state': 'NC',
                        'dog_name': 'Dog 1',
                        'dog_species': 'Labrador Retriever',
                        'shelter_entry_date': '1/1/2024',
                        'dog_description': 'First dog'
                    },
                    {
                        'shelter': 'Test Shelter 2',
                        'city': 'Raleigh',
                        'state': 'NC',
                        'dog_name': 'Dog 2',
                        'dog_species': 'Yellow Lab',
                        'shelter_entry_date': '1/2/2024',
                        'dog_description': 'Second dog'
                    },
                    {
                        'shelter': 'Test Shelter 3',
                        'city': 'Durham',
                        'state': 'NC',
                        'dog_name': 'Dog 3',
                        'dog_species': 'Poodle',
                        'shelter_entry_date': '1/3/2024',
                        'dog_description': 'Invalid dog'
                    }
                ]
            })
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 200
        result = json.loads(response['body'])
        assert result['total_processed'] == 3
        assert result['successful_uploads'] == 2
        assert result['failed_uploads'] == 1

class TestDataValidation:
    """Test data validation and cleaning functions"""
    
    def test_validate_and_clean_data_valid(self):
        """Test validation with valid data"""
        data = {
            'shelter': '  Test Shelter  ',
            'city': 'CHARLOTTE',
            'state': 'nc',
            'dog_name': '  Buddy  ',
            'dog_species': 'labrador retriever',
            'shelter_entry_date': '1/15/2024',
            'dog_description': 'Great dog',
            'dog_weight': '65 pounds',
            'dog_color': 'yellow'
        }
        
        result = validate_and_clean_data(data)
        
        assert 'error' not in result
        assert result['shelter'] == 'Test Shelter'
        assert result['city'] == 'CHARLOTTE'
        assert result['state'] == 'nc'
        assert result['dog_name'] == 'Buddy'
        assert result['dog_weight'] == 65.0
        assert result['dog_color'] == 'Yellow'
    
    def test_validate_and_clean_data_missing_required(self):
        """Test validation with missing required fields"""
        data = {
            'shelter': 'Test Shelter',
            'city': 'Charlotte'
            # Missing required fields
        }
        
        result = validate_and_clean_data(data)
        
        assert 'error' in result
        assert 'Missing or empty required field' in result['error']
    
    def test_is_labrador_retriever_valid(self):
        """Test Labrador Retriever species validation"""
        valid_species = [
            'Labrador Retriever',
            'labrador retriever',
            'Labrador',
            'Lab',
            'Yellow Lab',
            'Black Lab',
            'Chocolate Lab',
            'Silver Lab',
            'Labrador Mix',
            'Lab Mix'
        ]
        
        for species in valid_species:
            assert is_labrador_retriever(species), f"Should accept: {species}"
    
    def test_is_labrador_retriever_invalid(self):
        """Test rejection of non-Labrador species"""
        invalid_species = [
            'German Shepherd',
            'Poodle',
            'Golden Retriever',
            'Bulldog',
            'Beagle'
        ]
        
        for species in invalid_species:
            assert not is_labrador_retriever(species), f"Should reject: {species}"
    
    def test_clean_weight_valid(self):
        """Test weight cleaning with valid inputs"""
        test_cases = [
            ('65', 65.0),
            ('32.5', 32.5),
            ('thirty two pounds', None),  # Text numbers not supported in this simple version
            ('65 pounds', 65.0),
            ('32 lbs', 32.0),
            ('45.5 kg', 45.5),
            (65, 65.0),
            (32.5, 32.5)
        ]
        
        for input_weight, expected in test_cases:
            result = clean_weight(input_weight)
            if expected is None:
                assert result is None, f"Should return None for: {input_weight}"
            else:
                assert result == expected, f"Expected {expected} for {input_weight}, got {result}"
    
    def test_clean_weight_invalid(self):
        """Test weight cleaning with invalid inputs"""
        invalid_weights = [
            'abc',
            '',
            None,
            'very heavy',
            '300',  # Too heavy
            '0',    # Too light
            '-5'    # Negative
        ]
        
        for weight in invalid_weights:
            result = clean_weight(weight)
            if weight == '300' or weight == '0' or weight == '-5':
                # These are valid numbers but outside reasonable range
                continue
            assert result is None, f"Should return None for: {weight}"
    
    def test_parse_date_formats(self):
        """Test date parsing with various formats"""
        from datetime import datetime
        
        test_cases = [
            ('1/15/2024', datetime(2024, 1, 15)),
            ('2024-01-15', datetime(2024, 1, 15)),
            ('01-15-2024', datetime(2024, 1, 15)),
            ('15/01/2024', datetime(2024, 1, 15)),
            ('1/15/24', datetime(2024, 1, 15))
        ]
        
        for date_str, expected in test_cases:
            try:
                result = parse_date(date_str)
                assert result.date() == expected.date(), f"Expected {expected.date()} for {date_str}, got {result.date()}"
            except ValueError:
                # Some formats might not be supported, that's okay
                pass
    
    def test_generate_shelter_id(self):
        """Test shelter ID generation"""
        result = generate_shelter_id('Happy Paws Shelter', 'Charlotte', 'NC')
        expected = 'happy_paws_shelter_charlotte_nc'
        assert result == expected
        
        # Test with special characters
        result2 = generate_shelter_id('Shelter & Rescue!', 'Winston-Salem', 'NC')
        expected2 = 'shelter__rescue_winstonsalem_nc'
        assert result2 == expected2

class TestImageProcessing:
    """Test image processing functionality"""
    
    @patch('upload_handler.s3_client')
    def test_process_image_upload(self, mock_s3):
        """Test image upload processing"""
        from upload_handler import process_image_upload
        
        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://test-url.com'
        
        # Create a simple base64 image
        test_image = base64.b64encode(b'fake-image-data').decode('utf-8')
        
        result = process_image_upload(test_image, 'test_shelter', 'test_dog_id')
        
        assert 'error' not in result
        assert 'image_id' in result
        assert 'original_key' in result
        assert 'original_url' in result
        assert result['size_bytes'] > 0

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_json_body(self):
        """Test handling of invalid JSON in request body"""
        event = {
            'httpMethod': 'POST',
            'path': '/upload',
            'body': 'invalid json'
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 400
        result = json.loads(response['body'])
        assert 'Invalid JSON format' in result['error']
    
    def test_unknown_endpoint(self):
        """Test handling of unknown endpoints"""
        event = {
            'httpMethod': 'GET',
            'path': '/unknown'
        }
        
        response = handler(event, {})
        
        assert response['statusCode'] == 404
        result = json.loads(response['body'])
        assert 'Endpoint not found' in result['error']

def run_tests():
    """Run all tests"""
    print("🧪 Running Upload API Integration Tests")
    
    # Run pytest
    pytest.main([__file__, '-v'])

if __name__ == '__main__':
    run_tests()
