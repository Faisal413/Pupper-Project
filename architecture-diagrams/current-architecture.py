#!/usr/bin/env python3
"""
Pupper Application - Current Architecture Diagram
Generates AWS architecture diagram for the implemented components
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.network import APIGateway
from diagrams.aws.security import KMS, Cognito
from diagrams.aws.management import Cloudwatch
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users

def create_current_architecture():
    """Generate current state architecture diagram"""
    
    with Diagram("Pupper Dog Adoption - Current Architecture (50% Complete)", 
                 show=False, 
                 filename="pupper-current-architecture",
                 direction="TB"):
        
        # Users
        users = Users("Users")
        mobile = Mobile("React Frontend\n(Material-UI)")
        
        with Cluster("AWS Cloud"):
            # Authentication
            cognito = Cognito("Amazon Cognito\nUser Pool")
            
            # API Layer
            api_gateway = APIGateway("API Gateway\nREST API")
            
            # Compute Layer
            with Cluster("Lambda Functions"):
                dogs_lambda = Lambda("Dogs Handler\n(CRUD Operations)")
                upload_lambda = Lambda("Upload Handler\n(Presigned URLs)")
                image_processor = Lambda("Image Processor\n(Basic Resize)")
            
            # Storage Layer
            with Cluster("Data Storage"):
                s3_bucket = S3("S3 Bucket\nImage Storage")
                dogs_table = Dynamodb("DynamoDB\nDogs Table")
                interactions_table = Dynamodb("DynamoDB\nInteractions Table")
            
            # Security & Monitoring
            kms = KMS("KMS Key\nEncryption")
            cloudwatch = Cloudwatch("CloudWatch\nLogs & Monitoring")
        
        # Connections
        users >> mobile
        mobile >> Edge(label="Auth") >> cognito
        mobile >> Edge(label="API Calls") >> api_gateway
        
        api_gateway >> Edge(label="CRUD") >> dogs_lambda
        api_gateway >> Edge(label="Upload") >> upload_lambda
        
        dogs_lambda >> dogs_table
        dogs_lambda >> interactions_table
        dogs_lambda >> s3_bucket
        
        upload_lambda >> s3_bucket
        s3_bucket >> Edge(label="S3 Event") >> image_processor
        image_processor >> s3_bucket
        
        # Security connections
        dogs_table >> Edge(label="Encrypt") >> kms
        interactions_table >> Edge(label="Encrypt") >> kms
        
        # Monitoring
        dogs_lambda >> cloudwatch
        upload_lambda >> cloudwatch
        image_processor >> cloudwatch

if __name__ == "__main__":
    create_current_architecture()
    print("✅ Current architecture diagram generated: pupper-current-architecture.png")