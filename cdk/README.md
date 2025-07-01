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

### Security Features
- **KMS Encryption**: Dog names are encrypted using AWS KMS
- **Table Encryption**: DynamoDB tables encrypted with customer-managed KMS key
- **Point-in-time Recovery**: Enabled for data protection

### API Endpoints

#### Dogs
- `GET /dogs` - Get all dogs (with optional filters)
  - Query parameters: `state`, `min_weight`, `max_weight`, `color`
- `POST /dogs` - Create new dog entry
- `GET /dogs/{dog_id}` - Get specific dog (requires `shelter_id` query param)
- `PUT /dogs/{dog_id}` - Update dog (requires `shelter_id` query param)
- `DELETE /dogs/{dog_id}` - Delete dog (requires `shelter_id` query param)

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

### Get Dogs by State
```bash
curl "https://your-api-url/dogs?state=VA"
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

## Security Features

- **Dog Name Encryption**: All dog names encrypted with KMS before storage
- **Table Encryption**: DynamoDB tables encrypted at rest
- **CORS Configuration**: Proper CORS headers for web application integration

## Next Steps

This foundation supports:
1. ✅ Component 1: Database and REST API
2. Ready for Component 2: Observability & Monitoring (add unit tests, logging, tracing)
3. Ready for Component 3: Image Processing (add S3 bucket and image handling)
4. Ready for Component 5: Authentication (add Cognito integration)

The infrastructure is designed to handle the high-scale requirements mentioned in the project specifications with pay-per-request billing and proper indexing for efficient queries.

## Useful CDK Commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
