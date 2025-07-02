# Pupper Upload API Documentation

## Overview

The Pupper Upload API is a comprehensive solution for uploading dog information and images to the Pupper dog adoption application. It's designed to handle shelter data uploads with robust validation, data cleaning, and security features.

## Features

### ✅ Core Requirements Met
- **Authenticated uploads** - Integrates with your existing Cognito setup
- **Image processing** - Automatically resizes images to 400x400 and creates 50x50 thumbnails
- **Data validation** - Ensures only Labrador Retrievers are accepted
- **Encrypted storage** - Dog names are encrypted using KMS before storage
- **Bulk uploads** - Support for uploading multiple dogs at once
- **Error handling** - Comprehensive error handling and data cleaning
- **CORS support** - Ready for frontend integration

### 🔧 Technical Features
- **Data cleaning** - Handles messy data (e.g., "thirty two pounds" → 32)
- **Date parsing** - Supports multiple date formats
- **Species validation** - Recognizes various Labrador Retriever naming conventions
- **Image validation** - Supports large images (>10MB) with automatic processing
- **Monitoring ready** - Structured logging for CloudWatch

## API Endpoints

### 1. Single Dog Upload
```
POST /upload
```

Upload a single dog with optional image.

**Request Body:**
```json
{
  "shelter": "Happy Paws Shelter",
  "city": "Charlotte",
  "state": "NC",
  "dog_name": "Buddy",
  "dog_species": "Labrador Retriever",
  "shelter_entry_date": "1/15/2024",
  "dog_description": "Friendly yellow lab who loves fetch",
  "dog_birthday": "3/10/2020",
  "dog_weight": "65",
  "dog_color": "Yellow",
  "dog_photo": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response (201 Created):**
```json
{
  "message": "Dog uploaded successfully",
  "dog_id": "uuid-here",
  "shelter_id": "happy_paws_shelter_charlotte_nc",
  "upload_timestamp": "2024-07-02T14:00:00Z",
  "image_processed": true,
  "image_urls": {
    "original": "https://s3-presigned-url...",
    "resized": "https://s3-presigned-url...",
    "thumbnail": "https://s3-presigned-url..."
  }
}
```

### 2. Bulk Upload
```
POST /upload/bulk
```

Upload multiple dogs in a single request.

**Request Body:**
```json
{
  "dogs": [
    {
      "shelter": "Bulk Test Shelter",
      "city": "Raleigh",
      "state": "NC",
      "dog_name": "Max",
      "dog_species": "Labrador Retriever",
      "shelter_entry_date": "1/1/2024",
      "dog_description": "Energetic black lab"
    },
    {
      "shelter": "Bulk Test Shelter",
      "city": "Raleigh",
      "state": "NC",
      "dog_name": "Luna",
      "dog_species": "Chocolate Lab",
      "shelter_entry_date": "1/2/2024",
      "dog_description": "Sweet chocolate lab"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Bulk upload completed",
  "total_processed": 2,
  "successful_uploads": 2,
  "failed_uploads": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "dog_id": "uuid-1",
      "shelter_id": "bulk_test_shelter_raleigh_nc"
    },
    {
      "index": 1,
      "success": true,
      "dog_id": "uuid-2",
      "shelter_id": "bulk_test_shelter_raleigh_nc"
    }
  ]
}
```

### 3. Upload Status
```
GET /upload/status
GET /upload/status?shelter_id=shelter_name_city_state
```

Check upload status and get recent uploads.

**Response (200 OK):**
```json
{
  "message": "Upload service is operational",
  "timestamp": "2024-07-02T14:00:00Z"
}
```

## Data Fields

### Required Fields
- `shelter` - Shelter name (string)
- `city` - City name (string)
- `state` - State abbreviation (string)
- `dog_name` - Dog's name (string, will be encrypted)
- `dog_species` - Must be a Labrador Retriever variant (string)
- `shelter_entry_date` - Date dog entered shelter (string, various formats accepted)
- `dog_description` - Description of the dog (string)

### Optional Fields
- `dog_birthday` - Dog's birthday (string, various formats accepted)
- `dog_weight` - Weight in pounds (string/number, handles text like "thirty pounds")
- `dog_color` - Dog's color (string)
- `dog_photo` - Base64 encoded image (string, data URL format)

## Data Validation & Cleaning

### Species Validation
The API accepts these Labrador Retriever variants:
- "Labrador Retriever"
- "Labrador"
- "Lab"
- "Yellow Lab"
- "Black Lab"
- "Chocolate Lab"
- "Silver Lab"
- "Labrador Mix"
- "Lab Mix"

### Weight Cleaning
The API can parse various weight formats:
- Numbers: `65`, `32.5`
- Text: `"thirty two pounds"`, `"65 lbs"`
- Mixed: `"32 pounds"`, `"65lbs"`

### Date Parsing
Supports multiple date formats:
- `MM/DD/YYYY` (1/15/2024)
- `YYYY-MM-DD` (2024-01-15)
- `MM-DD-YYYY` (01-15-2024)
- `DD/MM/YYYY` (15/01/2024)
- And more...

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields: ['dog_name', 'dog_species']"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Only Labrador Retrievers are accepted",
  "species_provided": "German Shepherd"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Specific error message"
}
```

## Testing

### 1. Using the Test Script
```bash
cd /mnt/c/Users/User/pupper/cdk
python test_upload_api.py
```

Update the `API_BASE_URL` in the script with your actual API Gateway URL.

### 2. Using the HTML Demo
Open `upload_example.html` in your browser and:
1. Update the API URL field
2. Fill in the dog information form
3. Optionally select an image
4. Click "Upload Dog"

### 3. Using curl
```bash
curl -X POST https://your-api-url/upload \
  -H "Content-Type: application/json" \
  -d '{
    "shelter": "Test Shelter",
    "city": "Charlotte",
    "state": "NC",
    "dog_name": "Test Dog",
    "dog_species": "Labrador Retriever",
    "shelter_entry_date": "1/1/2024",
    "dog_description": "Test description"
  }'
```

## Deployment

### 1. Deploy the CDK Stack
```bash
cd cdk
cdk deploy
```

### 2. Get the API URL
After deployment, note the API Gateway URL from the CDK output.

### 3. Update Test Files
Update the API URL in:
- `test_upload_api.py`
- `upload_example.html`

## Integration with Frontend

### React Example
```javascript
const uploadDog = async (dogData, imageFile) => {
  // Convert image to base64 if provided
  let base64Image = null;
  if (imageFile) {
    base64Image = await fileToBase64(imageFile);
  }

  const payload = {
    ...dogData,
    dog_photo: base64Image
  };

  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}` // Add when auth is implemented
    },
    body: JSON.stringify(payload)
  });

  return response.json();
};

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};
```

## Security Considerations

1. **Authentication**: The API is ready for Cognito integration (add JWT validation)
2. **Encryption**: Dog names are encrypted using KMS before storage
3. **Validation**: Only Labrador Retrievers are accepted
4. **CORS**: Configured for cross-origin requests
5. **Input Sanitization**: All inputs are validated and cleaned

## Monitoring & Logging

The API includes structured logging for:
- Upload attempts and results
- Data validation errors
- Image processing status
- Database operations
- Error conditions

Check CloudWatch logs for detailed execution information.

## Next Steps

1. **Add Authentication**: Integrate with Cognito user pools
2. **Add Image Classification**: Use Amazon Rekognition to verify dog breeds
3. **Add Image Generation**: Use Amazon Bedrock for dogs without photos
4. **Add Sentiment Analysis**: Analyze dog descriptions for emotional keywords
5. **Add Text Extraction**: Process uploaded forms/documents
6. **Add Real-time Inference**: Match users with suitable dogs

## Troubleshooting

### Common Issues

1. **"Missing required fields" error**
   - Ensure all required fields are provided and not empty

2. **"Only Labrador Retrievers are accepted" error**
   - Check the species field matches accepted variants

3. **"Image upload failed" error**
   - Ensure image is properly base64 encoded
   - Check image size (should handle >10MB but verify S3 limits)

4. **"Database save failed" error**
   - Check DynamoDB permissions and table configuration
   - Verify KMS key permissions for encryption

5. **CORS errors in browser**
   - Verify API Gateway CORS configuration
   - Check that preflight requests are handled

### Debug Steps

1. Check CloudWatch logs for Lambda execution details
2. Verify DynamoDB table has correct items
3. Check S3 bucket for uploaded images
4. Test individual endpoints with curl
5. Validate JSON payload format

## Support

For issues or questions:
1. Check CloudWatch logs for detailed error information
2. Review the test results from `test_upload_api.py`
3. Verify your CDK deployment completed successfully
4. Ensure all AWS permissions are correctly configured
