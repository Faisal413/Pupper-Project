# Pupper Dog Adoption Application - CDK Stack

This CDK stack creates the infrastructure for the Pupper dog adoption application, including:

## Infrastructure Components

### DynamoDB Tables
1. **pupper-dogs**: Main table storing dog information
   - Partition Key: `shelter_id` (format: STATE#CITY#SHELTER_NAME)
   - Sort Key: `dog_id` (UUID)
   - GSI: StateIndex (for filtering by state)
   - GSI: SpeciesIndex (for filtering by species)

2. **pupper-user-interactions**: User interactions (wags/growls)
   - Partition Key: `user_id`
   - Sort Key: `dog_key` (format: shelter_id#dog_id)
   - GSI: DogInteractionsIndex (for querying interactions by dog)

### S3 Bucket
- **pupper-images-bucket**: Stores dog images
  - Original images
  - Standard size images (400x400)
  - Thumbnails (50x50)

### Lambda Functions
1. **DogsHandler**: Handles dog CRUD operations and API requests
2. **ImageProcessorHandler**: Processes uploaded images (resizing, thumbnails)

### Security Features
- **KMS Encryption**: Dog names are encrypted using AWS KMS
- **Table Encryption**: DynamoDB tables encrypted with customer-managed KMS key
- **Point-in-time Recovery**: Enabled for data protection
- **S3 Security**: Bucket configured with proper access controls

### API Endpoints

#### Dogs
- `GET /dogs` - Get all dogs (with optional filters)
  - Query parameters: `state`, `min_weight`, `max_weight`, `color`
- `POST /dogs` - Create new dog entry
- `GET /dogs/{dog_id}` - Get specific dog (requires `shelter_id` query param)
- `PUT /dogs/{dog_id}` - Update dog (requires `shelter_id` query param)
- `DELETE /dogs/{dog_id}` - Delete dog (requires `shelter_id` query param)

#### Images
- `POST /dogs/{dog_id}/images` - Upload image for a dog (requires `shelter_id` query param)
- `GET /dogs/{dog_id}/images` - Get all images for a dog (requires `shelter_id` query param)
- `GET /dogs/{dog_id}/images/{image_id}` - Get specific image (requires `shelter_id` query param)
- `DELETE /dogs/{dog_id}/images/{image_id}` - Delete image (requires `shelter_id` query param)

#### Interactions
- `POST /interactions` - Record user interaction (wag/growl)
- `GET /interactions` - Get user's interactions (requires `user_id` query param)

## Dog Data Schema

Required fields:
- `shelter`: Shelter name (e.g., "Arlington Shelter")
- `city`: City name (e.g., "Arlington")
- `state`: State abbreviation (e.g., "VA")
- `dog_name`: Dog's name (encrypted in storage)
- `species`: Must contain "Labrador" or "Lab"
- `description`: Dog description

Optional fields:
- `shelter_entry_date`: Date dog entered shelter
- `dog_birthday`: Dog's birthday
- `dog_weight`: Weight in pounds (handles string formats like "thirty two pounds")
- `dog_color`: Dog's color
- `images`: Array of image metadata (added when images are uploaded)

## Image Processing

The application supports uploading and processing images for dogs:

1. **Upload Process**:
   - Images are uploaded via the API as base64-encoded data
   - Original images are stored in S3
   - Images are automatically resized to standard (400x400) and thumbnail (50x50) sizes
   - Image metadata is stored in the dog's DynamoDB record

2. **Image Formats**:
   - Supported formats: JPG, JPEG, PNG, GIF
   - Maximum upload size: 10MB+

3. **Image Storage**:
   - Original images: `/dogs/{dog_id}/original/{image_id}.{ext}`
   - Standard images: `/dogs/{dog_id}/standard/{image_id}.png`
   - Thumbnails: `/dogs/{dog_id}/thumbnail/{image_id}.png`

4. **Image Metadata**:
   - `image_id`: Unique identifier for the image
   - `original_key`: S3 key for the original image
   - `standard_key`: S3 key for the standard image
   - `thumbnail_key`: S3 key for the thumbnail
   - `content_type`: MIME type of the original image
   - `created_at`: Timestamp when the image was uploaded
   - `original_filename`: Original filename provided during upload

## Deployment Instructions

1. **Install dependencies**:
   ```bash
   cd cdk
   pip install -e .
   ```

2. **Deploy the stack**:
   ```bash
   cdk deploy
   ```

3. **Test the API**:
   ```bash
   python test_api.py <API_GATEWAY_URL>
   ```

4. **Test image upload**:
   ```bash
   python test_image_upload.py <API_GATEWAY_URL> <PATH_TO_IMAGE>
   ```

## Example API Usage

### Create a Dog
```bash
curl -X POST https://your-api-url/dogs \
  -H "Content-Type: application/json" \
  -d '{
    "shelter": "Arlington Shelter",
    "city": "Arlington", 
    "state": "VA",
    "dog_name": "Buddy",
    "species": "Labrador Retriever",
    "description": "Friendly golden lab",
    "dog_weight": "45",
    "dog_color": "Golden"
  }'
```

### Upload an Image
```bash
curl -X POST "https://your-api-url/dogs/dog-uuid-here/images?shelter_id=VA%23ARLINGTON%23ARLINGTON_SHELTER" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "dog_photo.jpg",
    "image_data": "base64_encoded_image_data_here"
  }'
```

### Get Dog Images
```bash
curl "https://your-api-url/dogs/dog-uuid-here/images?shelter_id=VA%23ARLINGTON%23ARLINGTON_SHELTER"
```

### Record User Interaction
```bash
curl -X POST https://your-api-url/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "shelter_id": "VA#ARLINGTON#ARLINGTON_SHELTER",
    "dog_id": "dog-uuid-here",
    "interaction_type": "wag"
  }'
```

## Data Validation Features

- **Species Validation**: Only accepts dogs with "Labrador" or "Lab" in species field
- **Weight Parsing**: Handles various weight formats including text like "thirty two pounds"
- **Required Field Validation**: Ensures all required fields are present
- **Error Handling**: Comprehensive error responses for invalid data
- **Image Validation**: Validates image formats and sizes

## Security Features

- **Dog Name Encryption**: All dog names encrypted with KMS before storage
- **Table Encryption**: DynamoDB tables encrypted at rest
- **CORS Configuration**: Proper CORS headers for web application integration
- **S3 Security**: Bucket configured with proper access controls

## Next Steps

This foundation supports:
1. ✅ Component 1: Database and REST API
2. ✅ Component 2: Observability & Monitoring (add unit tests, logging, tracing)
3. ✅ Component 3: Image Processing (add S3 bucket and image handling)
4. Ready for Component 5: Authentication (add Cognito integration)

The infrastructure is designed to handle the high-scale requirements mentioned in the project specifications with pay-per-request billing and proper indexing for efficient queries.

## Useful CDK Commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
