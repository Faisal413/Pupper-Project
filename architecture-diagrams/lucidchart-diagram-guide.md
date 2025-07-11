# Pupper Current Architecture - Lucidchart Drawing Guide

## 🎯 **Exact Layout for Current State (50% Complete)**

### **Step 1: Create Layers (Top to Bottom)**

```
┌─────────────────────────────────────────────────────────────┐
│                        USERS LAYER                          │
│  👥 Users  →  📱 React Frontend (Material-UI)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                     │
│              🔐 Amazon Cognito User Pool                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       API LAYER                            │
│              🌐 Amazon API Gateway (REST)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE LAYER                           │
│  ⚡ Lambda: Dogs Handler  ⚡ Lambda: Upload Handler         │
│                                                            │
│           ⚡ Lambda: Image Processor                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                          │
│  🗄️ DynamoDB: Dogs Table    🗄️ DynamoDB: Interactions     │
│                                                            │
│              📦 S3 Bucket: Image Storage                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 SECURITY & MONITORING                       │
│        🔑 KMS Encryption    📊 CloudWatch Logs            │
└─────────────────────────────────────────────────────────────┘
```

## 📋 **Lucidchart Instructions**

### **1. Setup Canvas**
- Create new AWS Architecture diagram
- Enable AWS icon library
- Set canvas to landscape orientation

### **2. Place Components (Use AWS Icons)**

#### **Row 1: Users & Frontend**
- Place "Users" icon (generic user group)
- Place "Mobile/Web" icon for React Frontend
- Label: "React Frontend\n(Material-UI)"
- Connect with arrow →

#### **Row 2: Authentication**
- Place "Amazon Cognito" icon (red)
- Label: "Amazon Cognito\nUser Pool"
- Connect from Frontend with arrow ↓

#### **Row 3: API Gateway**
- Place "API Gateway" icon (purple)
- Label: "Amazon API Gateway\nREST API"
- Connect from Cognito with arrow ↓

#### **Row 4: Lambda Functions**
- Place 3 "Lambda" icons (orange) horizontally
- Labels:
  - "Dogs Handler\n(CRUD Operations)"
  - "Upload Handler\n(Presigned URLs)"
  - "Image Processor\n(Basic Resize)"
- Connect API Gateway to all 3 with arrows

#### **Row 5: Storage**
- Place 2 "DynamoDB" icons (blue)
- Place 1 "S3" icon (green)
- Labels:
  - "DynamoDB\nDogs Table"
  - "DynamoDB\nInteractions Table"
  - "S3 Bucket\nImage Storage"
- Connect Lambda functions to appropriate storage

#### **Row 6: Security & Monitoring**
- Place "KMS" icon (yellow)
- Place "CloudWatch" icon (purple)
- Labels:
  - "AWS KMS\nEncryption"
  - "Amazon CloudWatch\nLogs & Monitoring"

### **3. Add Connections**

#### **Main Flow (Solid Blue Arrows)**
```
Users → React Frontend → Cognito → API Gateway → Lambda Functions → Storage
```

#### **Security Connections (Dashed Red Lines)**
```
KMS ← DynamoDB Tables (both)
```

#### **Monitoring Connections (Dotted Green Lines)**
```
All Lambda Functions → CloudWatch
```

#### **Event Trigger (Orange Arrow)**
```
S3 Bucket → Image Processor Lambda
```

### **4. Add Labels & Annotations**

#### **Title Box (Top)**
```
🐕 Pupper Dog Adoption Platform
Current Architecture (50% Complete)
```

#### **Status Indicators**
- Add green checkmarks ✅ next to working components
- Add "WORKING" badges in green

#### **Component Details**
- Dogs Handler: "GET, POST, PUT /dogs"
- Upload Handler: "POST /upload/presigned"
- Image Processor: "S3 Event Triggered"
- DynamoDB: "Encrypted at Rest"
- S3: "CORS Enabled, Public Read"

### **5. Color Scheme**
- **Background**: Light gray (#F5F5F5)
- **AWS Cloud boundary**: Light blue rectangle
- **Arrows**: Blue (#0073BB)
- **Text**: Dark gray (#333333)
- **Status badges**: Green (#00C851)

### **6. Final Layout**
```
                    🐕 Pupper Dog Adoption Platform
                     Current Architecture (50% Complete)

👥 Users ──→ 📱 React Frontend
                    ↓
              🔐 Amazon Cognito
                    ↓
              🌐 API Gateway
                    ↓
    ⚡Dogs Handler  ⚡Upload Handler  ⚡Image Processor
         ↓               ↓                ↓
    🗄️Dogs Table   📦S3 Bucket ──→ (Event Trigger)
         ↓               ↓
    🗄️Interactions  🔑KMS Encryption
         ↓
    📊CloudWatch Monitoring
```

## 🎨 **Visual Tips**
- Use consistent spacing (50px between layers)
- Align components horizontally within each layer
- Use rounded rectangles for AWS services
- Add subtle shadows for depth
- Keep text readable (minimum 12pt font)