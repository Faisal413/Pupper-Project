# AWS Services Used in Pupper Application

## 🏗️ **Current Implementation (50% Complete)**

### **Compute Services**
- **AWS Lambda** (3 functions)
  - Dogs Handler - CRUD operations
  - Upload Handler - Presigned URL generation
  - Image Processor - Basic image resizing

### **Storage Services**
- **Amazon S3** - Image storage with versioning and CORS
- **Amazon DynamoDB** (2 tables)
  - pupper-dogs - Main dog data
  - pupper-user-interactions - User wag/growl tracking

### **Networking & API**
- **Amazon API Gateway** - REST API with CORS support

### **Security Services**
- **Amazon Cognito** - User pool for authentication
- **AWS KMS** - Customer-managed encryption keys

### **Monitoring & Management**
- **Amazon CloudWatch** - Logs and monitoring
- **AWS CDK** - Infrastructure as Code

## 🚀 **Future Implementation (Components 7-11)**

### **AI/ML Services**
- **Amazon Rekognition** - Image classification (Labrador detection)
- **Amazon Bedrock** - Generative AI for sentiment analysis and image generation
- **Amazon Textract** - Document text extraction
- **Amazon SageMaker** - Real-time inference for dog recommendations

### **Enhanced Security**
- **AWS WAF** - Web application firewall
- **Amazon GuardDuty** - Threat detection

### **Enhanced Monitoring**
- **AWS X-Ray** - Distributed tracing
- **Amazon EventBridge** - Event-driven architecture

## 📊 **Service Architecture Mapping**

### **Frontend Layer**
```
React App → Amazon Cognito (Auth) → API Gateway
```

### **API Layer**
```
API Gateway → Lambda Functions → DynamoDB/S3
```

### **Data Layer**
```
DynamoDB (Encrypted with KMS) + S3 (Image Storage)
```

### **AI/ML Layer (Future)**
```
Lambda → Rekognition/Bedrock/Textract/SageMaker → Results Storage
```

### **Monitoring Layer**
```
All Services → CloudWatch → Structured Logging
```

## 🎯 **For Diagram Creation**

Use these official AWS service icons:
- Lambda (orange)
- DynamoDB (blue) 
- S3 (green)
- API Gateway (purple)
- Cognito (red)
- KMS (yellow)
- CloudWatch (purple)
- Rekognition (orange)
- Bedrock (blue)
- Textract (orange)
- SageMaker (green)