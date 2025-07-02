from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_kms as kms,
    aws_s3 as s3
)


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # KMS Key for encrypting dog names
        encryption_key = kms.Key(
            self, 'PupperEncryptionKey',
            description='KMS key for encrypting dog names in Pupper app',
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY  # For development only
        )

        # S3 bucket for storing dog images
        images_bucket = s3.Bucket(
            self, 'PupperImagesBucket',
            bucket_name=f'pupper-images-{self.account}-{self.region}',
            encryption=s3.BucketEncryption.KMS,
            encryption_key=encryption_key,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_policy=False,
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            public_read_access=True
        )

        # DynamoDB table for storing dog information
        dogs_table = dynamodb.Table(
            self, 'DogsTable',
            table_name='pupper-dogs',
            partition_key=dynamodb.Attribute(
                name='shelter_id',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='dog_id',
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=encryption_key,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,  # For development only
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # GSI for querying by state
        dogs_table.add_global_secondary_index(
            index_name='StateIndex',
            partition_key=dynamodb.Attribute(
                name='state',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='created_at',
                type=dynamodb.AttributeType.STRING
            )
        )

        # GSI for querying by species (to filter Labrador Retrievers)
        dogs_table.add_global_secondary_index(
            index_name='SpeciesIndex',
            partition_key=dynamodb.Attribute(
                name='species',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='created_at',
                type=dynamodb.AttributeType.STRING
            )
        )

        # DynamoDB table for user interactions (wags/growls)
        interactions_table = dynamodb.Table(
            self, 'UserInteractionsTable',
            table_name='pupper-user-interactions',
            partition_key=dynamodb.Attribute(
                name='user_id',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='dog_key',  # Format: shelter_id#dog_id
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=encryption_key,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY  # For development only
        )

        # GSI for querying interactions by dog
        interactions_table.add_global_secondary_index(
            index_name='DogInteractionsIndex',
            partition_key=dynamodb.Attribute(
                name='dog_key',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='interaction_type',
                type=dynamodb.AttributeType.STRING
            )
        )

        # Lambda function for dog CRUD operations
        dogs_lambda = _lambda.Function(
            self, 'DogsHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions'),
            handler='dogs.handler',
            environment={
                'DOGS_TABLE_NAME': dogs_table.table_name,
                'INTERACTIONS_TABLE_NAME': interactions_table.table_name,
                'KMS_KEY_ID': encryption_key.key_id,
                'IMAGES_BUCKET_NAME': images_bucket.bucket_name
            },
            timeout=Duration.seconds(30)
        )
        
        # Lambda function for presigned URL upload handling
        upload_lambda = _lambda.Function(
            self, 'UploadHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions'),
            handler='upload_handler.handler',
            environment={
                'DOGS_TABLE_NAME': dogs_table.table_name,
                'KMS_KEY_ID': encryption_key.key_id,
                'IMAGES_BUCKET_NAME': images_bucket.bucket_name
            },
            timeout=Duration.seconds(30)
        )

        # Grant Lambda permissions to access DynamoDB tables
        dogs_table.grant_read_write_data(dogs_lambda)
        interactions_table.grant_read_write_data(dogs_lambda)
        dogs_table.grant_read_write_data(upload_lambda)
        
        # Grant Lambda permissions to use KMS key for encryption/decryption
        encryption_key.grant_encrypt_decrypt(dogs_lambda)
        encryption_key.grant_encrypt_decrypt(upload_lambda)
        
        # Grant Lambda permissions to access S3 bucket
        images_bucket.grant_read_write(dogs_lambda)
        images_bucket.grant_read_write(upload_lambda)

        # API Gateway
        api = apigw.RestApi(
            self, 'PupperApi',
            rest_api_name='Pupper API',
            description='API for Pupper dog adoption application',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key']
            )
        )

        # API Resources and Methods
        dogs_resource = api.root.add_resource('dogs')
        dogs_resource.add_method('GET', apigw.LambdaIntegration(dogs_lambda))  # Get all dogs with filters
        dogs_resource.add_method('POST', apigw.LambdaIntegration(dogs_lambda))  # Create new dog

        dog_resource = dogs_resource.add_resource('{dog_id}')
        dog_resource.add_method('GET', apigw.LambdaIntegration(dogs_lambda))  # Get specific dog
        dog_resource.add_method('PUT', apigw.LambdaIntegration(dogs_lambda))  # Update dog
        dog_resource.add_method('DELETE', apigw.LambdaIntegration(dogs_lambda))  # Delete dog

        # User interactions endpoints
        interactions_resource = api.root.add_resource('interactions')
        interactions_resource.add_method('POST', apigw.LambdaIntegration(dogs_lambda))  # Wag/Growl
        interactions_resource.add_method('GET', apigw.LambdaIntegration(dogs_lambda))  # Get user's interactions
        
        # Presigned URL upload endpoints
        upload_resource = api.root.add_resource('upload')
        presigned_resource = upload_resource.add_resource('presigned')
        complete_resource = upload_resource.add_resource('complete')
        
        presigned_resource.add_method('POST', apigw.LambdaIntegration(upload_lambda))  # Get presigned URL
        complete_resource.add_method('POST', apigw.LambdaIntegration(upload_lambda))   # Complete registration
        upload_resource.add_method('POST', apigw.LambdaIntegration(dogs_lambda))      # Existing upload

        # Output the API URL
        self.api_url = api.url