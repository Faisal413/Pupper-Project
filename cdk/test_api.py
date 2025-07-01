#!/usr/bin/env python3
"""
Simple test script to verify the Pupper API functionality
Run this after deploying your CDK stack
"""

import requests
import json
import sys

def test_api(api_url):
    """Test the Pupper API endpoints"""
    
    # Remove trailing slash if present
    api_url = api_url.rstrip('/')
    
    print(f"Testing API at: {api_url}")
    
    # Test data for a Labrador Retriever
    test_dog = {
        "shelter": "Arlington Shelter",
        "city": "Arlington",
        "state": "VA",
        "dog_name": "Buddy",
        "species": "Labrador Retriever",
        "description": "Friendly and energetic lab mix",
        "shelter_entry_date": "2024-01-15",
        "dog_birthday": "2020-05-10",
        "dog_weight": "45",
        "dog_color": "Golden"
    }
    
    try:
        # Test 1: Create a new dog
        print("\n1. Testing dog creation...")
        response = requests.post(f"{api_url}/dogs", json=test_dog)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            created_dog = response.json()['dog']
            shelter_id = created_dog['shelter_id']
            dog_id = created_dog['dog_id']
            print(f"✅ Dog created successfully! ID: {dog_id}")
            
            # Test 2: Get all dogs
            print("\n2. Testing get all dogs...")
            response = requests.get(f"{api_url}/dogs")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                dogs = response.json()['dogs']
                print(f"✅ Retrieved {len(dogs)} dogs")
            
            # Test 3: Get specific dog
            print("\n3. Testing get specific dog...")
            response = requests.get(f"{api_url}/dogs/{dog_id}?shelter_id={shelter_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Retrieved specific dog successfully")
            
            # Test 4: Filter by state
            print("\n4. Testing filter by state...")
            response = requests.get(f"{api_url}/dogs?state=VA")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                dogs = response.json()['dogs']
                print(f"✅ Retrieved {len(dogs)} dogs in VA")
            
            # Test 5: Test interaction (wag)
            print("\n5. Testing user interaction...")
            interaction_data = {
                "user_id": "test-user-123",
                "shelter_id": shelter_id,
                "dog_id": dog_id,
                "interaction_type": "wag"
            }
            response = requests.post(f"{api_url}/interactions", json=interaction_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                print("✅ Interaction recorded successfully")
            
            # Test 6: Get user interactions
            print("\n6. Testing get user interactions...")
            response = requests.get(f"{api_url}/interactions?user_id=test-user-123")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                interactions = response.json()['interactions']
                print(f"✅ Retrieved {len(interactions)} interactions")
        
        else:
            print(f"❌ Failed to create dog: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <API_URL>")
        print("Example: python test_api.py https://abc123.execute-api.us-east-1.amazonaws.com/prod")
        sys.exit(1)
    
    api_url = sys.argv[1]
    test_api(api_url)
