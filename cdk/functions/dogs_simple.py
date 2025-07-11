import json
import boto3
import os
import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
DOGS_TABLE_NAME = os.environ.get('DOGS_TABLE_NAME', 'pupper-dogs')
INTERACTIONS_TABLE_NAME = os.environ.get('INTERACTIONS_TABLE_NAME', 'pupper-user-interactions')

dogs_table = dynamodb.Table(DOGS_TABLE_NAME)
interactions_table = dynamodb.Table(INTERACTIONS_TABLE_NAME)

def handler(event, context):
    """Main Lambda handler"""
    try:
        logger.info(f"Event: {json.dumps(event)}")
        
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = event.get('body', '')
        
        # Parse request body
        request_body = {}
        if body:
            try:
                request_body = json.loads(body)
            except:
                pass
        
        logger.info(f"Method: {http_method}, Path: {path}")
        
        # Route requests
        if path == '/dogs':
            if http_method == 'GET':
                return get_dogs()
            elif http_method == 'POST':
                return create_dog(request_body)
        elif path == '/interactions':
            if http_method == 'POST':
                return create_interaction(request_body)
            elif http_method == 'GET':
                query_params = event.get('queryStringParameters') or {}
                return get_user_interactions(query_params)
        
        return create_response(404, {'error': 'Endpoint not found'})
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def get_dogs():
    """Get all dogs"""
    try:
        logger.info("Getting dogs from DynamoDB")
        response = dogs_table.scan()
        items = response.get('Items', [])
        
        logger.info(f"Found {len(items)} dogs")
        
        return create_response(200, {
            'dogs': items,
            'count': len(items)
        })
        
    except Exception as e:
        logger.error(f"Error getting dogs: {str(e)}")
        return create_response(500, {'error': f'Failed to get dogs: {str(e)}'})

def create_dog(dog_data):
    """Create a new dog"""
    try:
        logger.info(f"Creating dog: {dog_data}")
        
        # Validate required fields
        required_fields = ['shelter', 'city', 'state', 'dog_name', 'species', 'description']
        for field in required_fields:
            if field not in dog_data:
                return create_response(400, {'error': f'Missing field: {field}'})
        
        # Generate IDs
        shelter_id = f"{dog_data['state']}#{dog_data['city']}#{dog_data['shelter']}".replace(' ', '_').upper()
        dog_id = str(uuid.uuid4())
        
        # Create dog item
        dog_item = {
            'shelter_id': shelter_id,
            'dog_id': dog_id,
            'shelter': dog_data['shelter'],
            'city': dog_data['city'],
            'state': dog_data['state'],
            'dog_name': dog_data['dog_name'],  # Store plaintext for now
            'species': dog_data['species'],
            'description': dog_data['description'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields
        if 'dog_weight' in dog_data and dog_data['dog_weight']:
            try:
                weight = float(str(dog_data['dog_weight']).replace('pounds', '').replace('lbs', '').strip())
                dog_item['dog_weight'] = Decimal(str(weight))
            except:
                pass
                
        if 'dog_color' in dog_data and dog_data['dog_color']:
            dog_item['dog_color'] = dog_data['dog_color']
        
        # Save to DynamoDB
        dogs_table.put_item(Item=dog_item)
        
        logger.info(f"Dog created successfully: {dog_id}")
        
        return create_response(201, {
            'message': 'Dog created successfully',
            'dog': dog_item
        })
        
    except Exception as e:
        logger.error(f"Error creating dog: {str(e)}")
        return create_response(500, {'error': f'Failed to create dog: {str(e)}'})

def create_interaction(interaction_data):
    """Create user interaction"""
    try:
        required_fields = ['user_id', 'shelter_id', 'dog_id', 'interaction_type']
        for field in required_fields:
            if field not in interaction_data:
                return create_response(400, {'error': f'Missing field: {field}'})
        
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
            'message': 'Interaction recorded',
            'interaction': interaction_item
        })
        
    except Exception as e:
        logger.error(f"Error creating interaction: {str(e)}")
        return create_response(500, {'error': f'Failed to create interaction: {str(e)}'})

def get_user_interactions(query_params):
    """Get user interactions"""
    try:
        user_id = query_params.get('user_id')
        if not user_id:
            return create_response(400, {'error': 'user_id required'})
        
        response = interactions_table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        return create_response(200, {
            'interactions': response['Items'],
            'count': len(response['Items'])
        })
        
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        return create_response(500, {'error': f'Failed to get interactions: {str(e)}'})

def create_response(status_code, body):
    """Create API response"""
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