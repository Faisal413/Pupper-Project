import requests
import json

# Replace with your actual API Gateway URL
API_BASE_URL = "https://3wfbfr7110.execute-api.us-east-1.amazonaws.com/prod"

def test_presigned_url_generation():
    """Test Step 1: Generate presigned URL"""
    
    # Test data for presigned URL request
    test_data = {
        "filename": "test-dog.jpg",
        "file_size": 2048576,  # 2MB
        "content_type": "image/jpeg"
    }
    
    url = f"{API_BASE_URL}/upload/presigned"
    
    print("🧪 Testing Presigned URL Generation")
    print(f"📍 URL: {url}")
    print(f"📦 Request Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ SUCCESS! Presigned URL generated")
            print(f"📤 Upload URL: {response_data.get('upload_url', 'Not found')[:100]}...")
            print(f"🔑 S3 Key: {response_data.get('s3_key', 'Not found')}")
            print(f"⏰ Expires In: {response_data.get('expires_in', 'Not found')} seconds")
            return response_data
        else:
            print("❌ FAILED!")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Request Error: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"🚨 JSON Decode Error: {str(e)}")
        print(f"📄 Raw Response: {response.text}")
        return None

def test_invalid_requests():
    """Test error handling with invalid requests"""
    
    print("\n🧪 Testing Error Handling")
    print("-" * 50)
    
    # Test 1: Missing filename
    test_cases = [
        {
            "name": "Missing filename",
            "data": {"file_size": 1024, "content_type": "image/jpeg"}
        },
        {
            "name": "File too large",
            "data": {"filename": "huge.jpg", "file_size": 100*1024*1024, "content_type": "image/jpeg"}
        },
        {
            "name": "Invalid content type",
            "data": {"filename": "doc.pdf", "file_size": 1024, "content_type": "application/pdf"}
        }
    ]
    
    url = f"{API_BASE_URL}/upload/presigned"
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        try:
            response = requests.post(url, json=test_case['data'])
            print(f"📊 Status: {response.status_code}")
            if response.status_code != 200:
                print(f"✅ Expected error: {response.json().get('error', 'No error message')}")
            else:
                print("❌ Should have failed but didn't")
        except Exception as e:
            print(f"🚨 Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Presigned URL Tests")
    print("=" * 60)
    
    # Update the API_BASE_URL above with your actual URL
    if "YOUR-API-ID" in API_BASE_URL:
        print("❗ Please update API_BASE_URL in the script with your actual API Gateway URL")
        print("   You can find it in AWS Console > API Gateway > Your API > Stages")
        exit(1)
    
    # Test valid request
    result = test_presigned_url_generation()
    
    # Test error cases
    test_invalid_requests()
    
    print("\n" + "=" * 60)
    print("🏁 Tests Complete!")