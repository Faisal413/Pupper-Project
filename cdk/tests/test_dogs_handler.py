import json
import pytest
import boto3
from moto import mock_dynamodb, mock_kms
from unittest.mock import patch, MagicMock
import os
import sys

# Add the functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions'))

from dogs import handler, create_dog, get_dogs, create_interaction, encrypt_dog_name, decrypt_dog_name, parse_weight

class TestDogsHandler:
    """Test suite for the dogs Lambda handler"""
    
    @mock_dynamodb
    @mock_kms
    def setup_method(self):
        """Set up test environment before each test"""
        # Set up environment variables
        os.environ['DOGS_TABLE_NAME'] = 'test-pupper-dogs'
        os.environ['INTERACTIONS_TABLE_NAME'] = 'test-pupper-interactions'
        os.environ['KMS_KEY_ID'] = 'test-key-id'
        
        # Create mock DynamoDB tables
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create dogs table
        self.dogs_table = self.dynamodb.create_table(
            TableName='test-pupper-dogs',
            KeySchema=[
                {'AttributeName': 'shelter_id', 'KeyType': 'HASH'},
                {'AttributeName': 'dog_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'shelter_id', 'AttributeType': 'S'},
                {'AttributeName': 'dog_id', 'AttributeType': 'S'},
                {'AttributeName': 'state', 'AttributeType': 'S'},
                {'AttributeName': 'species', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'StateIndex',
                    'KeySchema': [
                        {'AttributeName': 'state', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        # Create interactions table
        self.interactions_table = self.dynamodb.create_table(
            TableName='test-pupper-interactions',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'dog_key', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'dog_key', 'AttributeType': 'S'}
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        # Create mock KMS client
        self.kms = boto3.client('kms', region_name='us-east-1')
        self.kms.create_key(Description='Test key')

    def test_create_dog_success(self):
        """Test successful dog creation"""
        dog_data = {
            "shelter": "Test Shelter",
            "city": "Test City",
            "state": "TX",
            "dog_name": "TestDog",
            "species": "Labrador Retriever",
            "description": "A good dog",
            "dog_weight": "50",
            "dog_color": "Brown"
        }
        
        with patch('dogs.encrypt_dog_name', return_value='encrypted_name'):
            result = create_dog(dog_data)
        
        assert result['statusCode'] == 201
        response_body = json.loads(result['body'])
        assert response_body['message'] == 'Dog created successfully'
        assert response_body['dog']['dog_name'] == 'TestDog'
        assert response_body['dog']['species'] == 'Labrador Retriever'

    def test_create_dog_missing_required_field(self):
        """Test dog creation with missing required field"""
        dog_data = {
            "shelter": "Test Shelter",
            "city": "Test City",
            "state": "TX",
            # Missing dog_name
            "species": "Labrador Retriever",
            "description": "A good dog"
        }
        
        result = create_dog(dog_data)
        
        assert result['statusCode'] == 400
        response_body = json.loads(result['body'])
        assert 'Missing required field' in response_body['error']

    def test_create_dog_non_labrador(self):
        """Test rejection of non-Labrador dogs"""
        dog_data = {
            "shelter": "Test Shelter",
            "city": "Test City",
            "state": "TX",
            "dog_name": "TestDog",
            "species": "German Shepherd",  # Not a Labrador
            "description": "A good dog"
        }
        
        result = create_dog(dog_data)
        
        assert result['statusCode'] == 400
        response_body = json.loads(result['body'])
        assert 'Only Labrador Retrievers are accepted' in response_body['error']

    def test_parse_weight_various_formats(self):
        """Test weight parsing from different formats"""
        assert parse_weight("45") == 45.0
        assert parse_weight("thirty two pounds") == 32.0
        assert parse_weight("25.5") == 25.5
        assert parse_weight(30) == 30.0
        assert parse_weight("invalid") is None

    def test_create_interaction_success(self):
        """Test successful interaction creation"""
        interaction_data = {
            "user_id": "test-user",
            "shelter_id": "TX#TEST_CITY#TEST_SHELTER",
            "dog_id": "test-dog-id",
            "interaction_type": "wag"
        }
        
        result = create_interaction(interaction_data)
        
        assert result['statusCode'] == 201
        response_body = json.loads(result['body'])
        assert response_body['message'] == 'Interaction recorded successfully'

    def test_create_interaction_invalid_type(self):
        """Test interaction creation with invalid type"""
        interaction_data = {
            "user_id": "test-user",
            "shelter_id": "TX#TEST_CITY#TEST_SHELTER",
            "dog_id": "test-dog-id",
            "interaction_type": "invalid"  # Should be 'wag' or 'growl'
        }
        
        result = create_interaction(interaction_data)
        
        assert result['statusCode'] == 400
        response_body = json.loads(result['body'])
        assert 'interaction_type must be "wag" or "growl"' in response_body['error']

    def test_handler_routing(self):
        """Test main handler routing"""
        # Test GET /dogs
        event = {
            'httpMethod': 'GET',
            'path': '/dogs',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        with patch('dogs.get_dogs') as mock_get_dogs:
            mock_get_dogs.return_value = {'statusCode': 200, 'body': '{"dogs": []}'}
            result = handler(event, {})
            mock_get_dogs.assert_called_once()

    def test_handler_invalid_endpoint(self):
        """Test handler with invalid endpoint"""
        event = {
            'httpMethod': 'GET',
            'path': '/invalid',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        result = handler(event, {})
        
        assert result['statusCode'] == 404
        response_body = json.loads(result['body'])
        assert response_body['error'] == 'Endpoint not found'

    @patch('dogs.kms')
    def test_encrypt_decrypt_dog_name(self, mock_kms):
        """Test dog name encryption and decryption"""
        # Mock KMS responses
        mock_kms.encrypt.return_value = {
            'CiphertextBlob': b'encrypted_data'
        }
        mock_kms.decrypt.return_value = {
            'Plaintext': b'TestDog'
        }
        
        # Test encryption
        encrypted = encrypt_dog_name('TestDog')
        assert encrypted is not None
        
        # Test decryption
        decrypted = decrypt_dog_name(encrypted)
        assert decrypted == 'TestDog'

class TestAPIIntegration:
    """Integration tests for the complete API"""
    
    def test_api_cors_headers(self):
        """Test that API responses include proper CORS headers"""
        event = {
            'httpMethod': 'GET',
            'path': '/dogs',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        with patch('dogs.get_dogs') as mock_get_dogs:
            mock_get_dogs.return_value = {'statusCode': 200, 'body': '{"dogs": []}'}
            result = handler(event, {})
            
            headers = result.get('headers', {})
            assert headers.get('Access-Control-Allow-Origin') == '*'
            assert 'Access-Control-Allow-Headers' in headers
            assert 'Access-Control-Allow-Methods' in headers

    def test_error_handling(self):
        """Test error handling in handler"""
        event = {
            'httpMethod': 'POST',
            'path': '/dogs',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': 'invalid json'  # This should cause a JSON decode error
        }
        
        result = handler(event, {})
        
        assert result['statusCode'] == 400
        response_body = json.loads(result['body'])
        assert 'Invalid JSON' in response_body['error']

if __name__ == '__main__':
    pytest.main([__file__])
