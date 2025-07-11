# 🐕 Dog Adoption App - AWS Deployment Checklist

## Prerequisites
- [ ] AWS Account created
- [ ] AWS CLI installed and configured
- [ ] React app built for production (`npm run build`)

## 📦 S3 Setup

### Create S3 Bucket
- [ ] **Create bucket**
  ```bash
  aws s3 mb s3://your-dog-app-bucket-name --region us-east-1
  ```
- [ ] **Enable static website hosting**
  ```bash
  aws s3 website s3://your-dog-app-bucket-name --index-document index.html --error-document error.html
  ```

### Upload Files
- [ ] **Upload build files**
  ```bash
  aws s3 sync ./build s3://your-dog-app-bucket-name --delete
  ```
- [ ] **Set public read permissions**
  ```bash
  aws s3api put-bucket-policy --bucket your-dog-app-bucket-name --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::your-dog-app-bucket-name/*"
      }
    ]
  }'
  ```

### Security Configuration
- [ ] **Block public ACLs** (keep bucket policy only)
- [ ] **Enable versioning** (optional)
- [ ] **Configure CORS** for API calls
  ```json
  [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": []
    }
  ]
  ```

## 🌐 CloudFront Setup

### Create Distribution
- [ ] **Create CloudFront distribution**
  ```bash
  aws cloudfront create-distribution --distribution-config '{
    "CallerReference": "dog-app-'$(date +%s)'",
    "Origins": {
      "Quantity": 1,
      "Items": [
        {
          "Id": "S3-your-dog-app-bucket-name",
          "DomainName": "your-dog-app-bucket-name.s3.amazonaws.com",
          "S3OriginConfig": {
            "OriginAccessIdentity": ""
          }
        }
      ]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "S3-your-dog-app-bucket-name",
      "ViewerProtocolPolicy": "redirect-to-https",
      "TrustedSigners": {
        "Enabled": false,
        "Quantity": 0
      },
      "ForwardedValues": {
        "QueryString": false,
        "Cookies": {"Forward": "none"}
      }
    },
    "Comment": "Dog Adoption App Distribution",
    "Enabled": true
  }'
  ```

### SSL Certificate
- [ ] **Request SSL certificate** (AWS Certificate Manager)
  ```bash
  aws acm request-certificate --domain-name yourdomain.com --validation-method DNS --region us-east-1
  ```
- [ ] **Validate certificate** (add DNS records)
- [ ] **Associate certificate** with CloudFront distribution

### Configure Error Pages
- [ ] **Set custom error pages**
  - 403 → /index.html (for SPA routing)
  - 404 → /index.html (for SPA routing)

## 🌍 Custom Domain (Optional)

### Route 53 Setup
- [ ] **Register domain** or transfer to Route 53
- [ ] **Create hosted zone**
- [ ] **Create A record** pointing to CloudFront distribution
  ```bash
  aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "yourdomain.com",
          "Type": "A",
          "AliasTarget": {
            "DNSName": "your-cloudfront-domain.cloudfront.net",
            "EvaluateTargetHealth": false,
            "HostedZoneId": "Z2FDTNDATAQYW2"
          }
        }
      }
    ]
  }'
  ```

## 🚀 CI/CD Pipeline (Optional)

### GitHub Actions Setup
- [ ] **Create `.github/workflows/deploy.yml`**
  ```yaml
  name: Deploy to AWS
  on:
    push:
      branches: [main]
  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - name: Setup Node.js
          uses: actions/setup-node@v2
          with:
            node-version: '18'
        - name: Install dependencies
          run: npm install
        - name: Build
          run: npm run build
        - name: Deploy to S3
          env:
            AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
            AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          run: |
            aws s3 sync build/ s3://your-dog-app-bucket-name --delete
            aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
  ```

### CodePipeline Setup
- [ ] **Create CodePipeline**
- [ ] **Connect GitHub repository**
- [ ] **Configure build stage** (CodeBuild)
- [ ] **Configure deploy stage** (S3 + CloudFront invalidation)

## 🔒 Security Best Practices

- [ ] **Use IAM roles** instead of access keys when possible
- [ ] **Enable CloudTrail** for audit logging
- [ ] **Set up CloudWatch** for monitoring
- [ ] **Configure WAF** for additional security (optional)
- [ ] **Enable S3 access logging**
- [ ] **Use least privilege** IAM policies

## 💰 Cost Estimates (Monthly)

### Basic Setup
- [ ] **S3 Storage**: ~$0.50 (for 20GB)
- [ ] **S3 Requests**: ~$0.10 (for 10K requests)
- [ ] **CloudFront**: ~$1.00 (for 10GB transfer)
- [ ] **Route 53**: ~$0.50 (hosted zone)
- [ ] **SSL Certificate**: FREE (AWS Certificate Manager)

### **Total Estimated Cost: ~$2-5/month**

## 📋 Testing Checklist

- [ ] **Test S3 website URL** works
- [ ] **Test CloudFront URL** works
- [ ] **Test custom domain** (if configured)
- [ ] **Test HTTPS** redirect works
- [ ] **Test SPA routing** (refresh on any page)
- [ ] **Test mobile responsiveness**
- [ ] **Test API calls** work from deployed app

## 🛠️ Useful Commands

### Build and Deploy
```bash
# Build React app
npm run build

# Sync to S3
aws s3 sync build/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

### Monitoring
```bash
# Check S3 bucket contents
aws s3 ls s3://your-bucket-name --recursive

# Get CloudFront distribution info
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID
```

## 🎯 Quick Start Commands

```bash
# 1. Build your app
npm run build

# 2. Create and configure S3 bucket
aws s3 mb s3://my-dog-app-$(date +%s)
aws s3 website s3://my-dog-app-$(date +%s) --index-document index.html

# 3. Upload files
aws s3 sync build/ s3://my-dog-app-$(date +%s) --delete

# 4. Make bucket public
aws s3api put-bucket-policy --bucket my-dog-app-$(date +%s) --policy file://bucket-policy.json

# 5. Create CloudFront distribution (use AWS Console for easier setup)
```

---

**🎉 Congratulations!** Your dog adoption app is now live on AWS!

**Next Steps:**
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Plan for scaling (if needed)
- [ ] Set up staging environment