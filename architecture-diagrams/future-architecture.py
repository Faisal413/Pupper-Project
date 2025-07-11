#!/usr/bin/env python3
"""
Pupper Application - Future Architecture Diagram
Shows complete architecture with all 11 components
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.network import APIGateway
from diagrams.aws.security import KMS, Cognito
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Rekognition, Bedrock, Textract, SagemakerModel
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users

def create_future_architecture():
    """Generate future state architecture diagram"""
    
    with Diagram("Pupper Dog Adoption - Future Architecture (Complete Vision)", 
                 show=False, 
                 filename="pupper-future-architecture",
                 direction="TB"):
        
        # Users
        users = Users("Users")
        mobile = Mobile("React Frontend\n(Enhanced UI)")
        
        with Cluster("AWS Cloud"):
            # Authentication
            cognito = Cognito("Amazon Cognito\nUser Pool + MFA")
            
            # API Layer
            api_gateway = APIGateway("API Gateway\nSecured REST API")
            
            # Core Compute Layer
            with Cluster("Core Lambda Functions"):
                dogs_lambda = Lambda("Dogs Handler\n(CRUD + Security)")
                upload_lambda = Lambda("Upload Handler\n(Enhanced Upload)")
                image_processor = Lambda("Image Processor\n(High-Quality Resize)")
            
            # AI/ML Compute Layer
            with Cluster("AI/ML Lambda Functions"):
                classifier = Lambda("Image Classifier\n(Labrador Detection)")
                generator = Lambda("Image Generator\n(Amazon Nova)")
                sentiment = Lambda("Sentiment Analyzer\n(Bedrock)")
                extractor = Lambda("Text Extractor\n(Document Processing)")
                recommender = Lambda("Recommendation Engine\n(Real-time Inference)")
            
            # Storage Layer
            with Cluster("Data Storage"):
                s3_bucket = S3("S3 Bucket\nMulti-tier Storage")
                dogs_table = Dynamodb("DynamoDB\nDogs + Metadata")
                interactions_table = Dynamodb("DynamoDB\nUser Interactions")
                ml_table = Dynamodb("DynamoDB\nML Results")
            
            # AI/ML Services
            with Cluster("AI/ML Services"):
                rekognition = Rekognition("Amazon Rekognition\nImage Classification")
                bedrock = Bedrock("Amazon Bedrock\nSentiment Analysis")
                textract = Textract("Amazon Textract\nDocument Processing")
                sagemaker = SagemakerModel("SageMaker\nRecommendation Model")
            
            # Security & Monitoring
            kms = KMS("KMS Key\nEnd-to-End Encryption")
            cloudwatch = Cloudwatch("CloudWatch\nComprehensive Monitoring")
        
        # User Flow
        users >> mobile
        mobile >> Edge(label="Secure Auth") >> cognito
        mobile >> Edge(label="Protected API") >> api_gateway
        
        # Core API Flow
        api_gateway >> dogs_lambda
        api_gateway >> upload_lambda
        
        # Data Storage
        dogs_lambda >> dogs_table
        dogs_lambda >> interactions_table
        dogs_lambda >> ml_table
        
        # Image Processing Pipeline
        upload_lambda >> s3_bucket
        s3_bucket >> Edge(label="S3 Event") >> image_processor
        s3_bucket >> Edge(label="Classification") >> classifier
        s3_bucket >> Edge(label="Sentiment") >> sentiment
        
        # AI/ML Integrations
        classifier >> rekognition
        generator >> bedrock
        sentiment >> bedrock
        extractor >> textract
        recommender >> sagemaker
        
        # AI Results Storage
        classifier >> ml_table
        generator >> s3_bucket
        sentiment >> ml_table
        extractor >> dogs_table
        recommender >> interactions_table
        
        # Security
        dogs_table >> kms
        interactions_table >> kms
        ml_table >> kms
        
        # Monitoring
        [dogs_lambda, upload_lambda, image_processor, 
         classifier, generator, sentiment, extractor, recommender] >> cloudwatch

if __name__ == "__main__":
    create_future_architecture()
    print("✅ Future architecture diagram generated: pupper-future-architecture.png")