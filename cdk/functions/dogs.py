import json
import boto3
import os
import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
import base64
from typing import Dict, Any, Optional

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
kms = boto3.client('kms')

# Environment variables
DOGS_TABLE_NAME = os.environ['DOGS_TABLE_NAME']
INTERACTIONS_TABLE_NAME = os.environ['INTERACTIONS_TABLE_NAME']
KMS_KEY_ID = os.environ['KMS_KEY_ID']

dogs_table = dynamodb.Table(DOGS_TABLE_NAME)
interactions_table = dynamodb.Table(INTERACTIONS_TABLE_NAME)

def handler(event, context):
    """
    Main Lambda handler for dog-related operations
    """
    request_id = context.aws_request_id if context else str(uuid.uuid4())
    
    # Structured logging
    logger.info("Request started", extra={
        "request_id": request_id,
        "http_method": event.get('httpMethod'),
        "path": event.get('path'),
        "user_agent": event.get('headers', {}).get('User-Agent', 'Unknown')
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
