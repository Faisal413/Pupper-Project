#!/usr/bin/env python3
import argparse
import base64
import json
import os
import requests
import time
import uuid
from typing import Dict, Any, Optional

def create_dog(api_url: str) -> Dict[str, Any]:
    """Create a test dog for image upload"""
    dog_data = {
        "shelter": "Test Shelter",
        "city": "Test City",
        "state": "TX",
        "dog_name": "Image Test Dog",
        "species": "Labrador Retriever",
        "description": "A test dog for image upload",
        "dog_weight": "45",
        "dog_color": "Golden"
    }
    
    response = requests.post(f"{api_url}/dogs", json=dog_data)
    if response.status_code != 201:
        print(f"Failed to create dog: {response.text}")
        exit(1)
    
    return response.json()

def upload_image(api_url: str, dog_id: str, shelter_id: str, image_path: str) -> Dict[str, Any]:
    """Upload an image for a dog"""
    # Read image file and encode as base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Prepare request data
    image_data = {
        "filename": os.path.basename(image_path),
        "image_data": encoded_string
    }
    
    # Upload image
    response = requests.post(
        f"{api_url}/dogs/{dog_id}/images",
        json=image_data,
        params={"shelter_id": shelter_id}
    )
    
    if response.status_code not in [200, 201, 202]:
        print(f"Failed to upload image: {response.text}")
        exit(1)
    
    return response.json()

def get_dog_images(api_url: str, dog_id: str, shelter_id: str) -> Dict[str, Any]:
    """Get all images for a dog"""
    response = requests.get(
        f"{api_url}/dogs/{dog_id}/images",
        params={"shelter_id": shelter_id}
    )
    
    if response.status_code != 200:
        print(f"Failed to get dog images: {response.text}")
        exit(1)
    
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Test image upload for Pupper app')
    parser.add_argument('api_url', help='API Gateway URL')
    parser.add_argument('image_path', help='Path to image file')
    args = parser.parse_args()
    
    # Create a test dog
    print("Creating test dog...")
    dog = create_dog(args.api_url)
    dog_id = dog['dog_id']
    shelter_id = dog['shelter_id']
    print(f"Created dog with ID: {dog_id}")
    print(f"Shelter ID: {shelter_id}")
    
    # Upload image
    print(f"Uploading image: {args.image_path}...")
    upload_result = upload_image(args.api_url, dog_id, shelter_id, args.image_path)
    print(f"Upload response: {json.dumps(upload_result, indent=2)}")
    
    # Wait for processing
    print("Waiting for image processing (10 seconds)...")
    time.sleep(10)
    
    # Get dog images
    print("Getting dog images...")
    images = get_dog_images(args.api_url, dog_id, shelter_id)
    print(f"Images: {json.dumps(images, indent=2)}")
    
    if 'images' in images and images['images']:
        print("\n✅ Image processing successful!")
        print(f"Original image: {images['images'][0]['original_url']}")
        print(f"Standard image (400x400): {images['images'][0]['standard_url']}")
        print(f"Thumbnail (50x50): {images['images'][0]['thumbnail_url']}")
    else:
        print("\n❌ Image processing failed or not completed yet.")
        print("Try running the script again with the same dog ID to check if processing completed.")

if __name__ == "__main__":
    main()
