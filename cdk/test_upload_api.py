#!/usr/bin/env python3
"""
Test script for the Pupper Upload API
Tests various upload scenarios including valid uploads, invalid data, and edge cases
"""

import json
import base64
import requests
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "https://your-api-gateway-url.amazonaws.com/prod"  # Update with your actual API URL
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"
BULK_UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/bulk"
STATUS_ENDPOINT = f"{API_BASE_URL}/upload/status"

def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Warning: Image file {image_path} not found. Using placeholder.")
        # Return a small placeholder base64 image
        return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"

def test_valid_single_upload():
    """Test valid single dog upload"""
    print("\n=== Testing Valid Single Upload ===")
    
    # Get base64 encoded image
    image_data = encode_image_to_base64("cute.jpg")
    
    test_data = {
        "shelter": "Happy Paws Shelter",
        "city": "Charlotte",
        "state": "NC",
        "dog_name": "Buddy",
        "dog_species": "Labrador Retriever",
        "shelter_entry_date": "1/15/2024",
        "dog_description": "Friendly and energetic yellow lab who loves to play fetch",
        "dog_birthday": "3/10/2020",
        "dog_weight": "65",
        "dog_color": "Yellow",
        "dog_photo": image_data
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Valid upload test PASSED")
            return response.json().get('dog_id')
        else:
            print("❌ Valid upload test FAILED")
            return None
            
    except Exception as e:
        print(f"❌ Error in valid upload test: {str(e)}")
        return None

def test_invalid_species_upload():
    """Test upload with non-Labrador Retriever"""
    print("\n=== Testing Invalid Species Upload ===")
    
    test_data = {
        "shelter": "City Animal Shelter",
        "city": "Raleigh",
        "state": "NC",
        "dog_name": "Rex",
        "dog_species": "German Shepherd",  # Not a Labrador Retriever
        "shelter_entry_date": "2/1/2024",
        "dog_description": "Great guard dog"
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 422:
            print("✅ Invalid species test PASSED")
        else:
            print("❌ Invalid species test FAILED")
            
    except Exception as e:
        print(f"❌ Error in invalid species test: {str(e)}")

def test_missing_required_fields():
    """Test upload with missing required fields"""
    print("\n=== Testing Missing Required Fields ===")
    
    test_data = {
        "shelter": "Incomplete Shelter",
        "city": "Durham",
        # Missing state, dog_name, dog_species, etc.
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ Missing fields test PASSED")
        else:
            print("❌ Missing fields test FAILED")
            
    except Exception as e:
        print(f"❌ Error in missing fields test: {str(e)}")

def test_data_cleaning():
    """Test data cleaning and validation"""
    print("\n=== Testing Data Cleaning ===")
    
    test_data = {
        "shelter": "  Messy Data Shelter  ",
        "city": "WINSTON-SALEM",
        "state": "nc",
        "dog_name": "  Messy Name  ",
        "dog_species": "yellow labrador retriever",
        "shelter_entry_date": "03/15/2024",
        "dog_description": "Good dog with messy data",
        "dog_weight": "thirty two pounds",  # Text weight
        "dog_color": "golden yellow"
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Data cleaning test PASSED")
        else:
            print("❌ Data cleaning test FAILED")
            
    except Exception as e:
        print(f"❌ Error in data cleaning test: {str(e)}")

def test_bulk_upload():
    """Test bulk upload functionality"""
    print("\n=== Testing Bulk Upload ===")
    
    dogs_data = [
        {
            "shelter": "Bulk Test Shelter",
            "city": "Asheville",
            "state": "NC",
            "dog_name": "Max",
            "dog_species": "Labrador Retriever",
            "shelter_entry_date": "1/1/2024",
            "dog_description": "Energetic black lab"
        },
        {
            "shelter": "Bulk Test Shelter",
            "city": "Asheville",
            "state": "NC",
            "dog_name": "Luna",
            "dog_species": "Chocolate Labrador",
            "shelter_entry_date": "1/2/2024",
            "dog_description": "Sweet chocolate lab"
        },
        {
            "shelter": "Bulk Test Shelter",
            "city": "Asheville",
            "state": "NC",
            "dog_name": "Invalid Dog",
            "dog_species": "Poodle",  # Should be rejected
            "shelter_entry_date": "1/3/2024",
            "dog_description": "Should be rejected"
        }
    ]
    
    bulk_data = {"dogs": dogs_data}
    
    try:
        response = requests.post(BULK_UPLOAD_ENDPOINT, json=bulk_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('successful_uploads') == 2 and result.get('failed_uploads') == 1:
                print("✅ Bulk upload test PASSED")
            else:
                print("❌ Bulk upload test FAILED - unexpected results")
        else:
            print("❌ Bulk upload test FAILED")
            
    except Exception as e:
        print(f"❌ Error in bulk upload test: {str(e)}")

def test_upload_status():
    """Test upload status endpoint"""
    print("\n=== Testing Upload Status ===")
    
    try:
        # Test general status
        response = requests.get(STATUS_ENDPOINT)
        print(f"General Status - Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test shelter-specific status
        shelter_response = requests.get(f"{STATUS_ENDPOINT}?shelter_id=happy_paws_shelter_charlotte_nc")
        print(f"\nShelter Status - Status Code: {shelter_response.status_code}")
        print(f"Response: {json.dumps(shelter_response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Upload status test PASSED")
        else:
            print("❌ Upload status test FAILED")
            
    except Exception as e:
        print(f"❌ Error in upload status test: {str(e)}")

def test_edge_cases():
    """Test various edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    # Test with minimal valid data
    minimal_data = {
        "shelter": "Minimal Shelter",
        "city": "Greensboro",
        "state": "NC",
        "dog_name": "Min",
        "dog_species": "Lab",
        "shelter_entry_date": "1/1/2024",
        "dog_description": "Minimal data test"
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, json=minimal_data)
        print(f"Minimal Data - Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test with invalid date format
        invalid_date_data = minimal_data.copy()
        invalid_date_data["shelter_entry_date"] = "invalid-date"
        
        response2 = requests.post(UPLOAD_ENDPOINT, json=invalid_date_data)
        print(f"\nInvalid Date - Status Code: {response2.status_code}")
        print(f"Response: {json.dumps(response2.json(), indent=2)}")
        
        if response.status_code == 201 and response2.status_code == 400:
            print("✅ Edge cases test PASSED")
        else:
            print("❌ Edge cases test FAILED")
            
    except Exception as e:
        print(f"❌ Error in edge cases test: {str(e)}")

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n=== Testing CORS Preflight ===")
    
    try:
        response = requests.options(UPLOAD_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS preflight test PASSED")
        else:
            print("❌ CORS preflight test FAILED")
            
    except Exception as e:
        print(f"❌ Error in CORS preflight test: {str(e)}")

def main():
    """Run all tests"""
    print("🐕 Starting Pupper Upload API Tests 🐕")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Check if API URL is configured
    if "your-api-gateway-url" in API_BASE_URL:
        print("\n⚠️  WARNING: Please update API_BASE_URL with your actual API Gateway URL")
        print("You can find this URL in your CDK deployment output or AWS Console")
        return
    
    # Run all tests
    test_cors_preflight()
    test_valid_single_upload()
    test_invalid_species_upload()
    test_missing_required_fields()
    test_data_cleaning()
    test_bulk_upload()
    test_upload_status()
    test_edge_cases()
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Review test results above")
    print("2. Check CloudWatch logs for detailed Lambda execution logs")
    print("3. Verify data in DynamoDB and S3 bucket")
    print("4. Test with your React frontend application")

if __name__ == "__main__":
    main()
