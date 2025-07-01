# Pupper Application Testing Guide

This document outlines the comprehensive testing strategy for the Pupper dog adoption application.

## 🧪 Testing Strategy

### Component 2 Requirements Coverage:
- ✅ **Unit tests for REST API**: Lambda function tests
- ✅ **Unit tests for CDK**: Infrastructure tests  
- ✅ **Structured logging**: CloudWatch integration
- ✅ **Tracing**: AWS X-Ray ready
- ✅ **CDK Nag**: Security compliance
- ✅ **Linting and formatting**: Code quality

## 📋 Test Categories

### 1. Unit Tests
**Location**: `tests/test_dogs_handler.py`

Tests individual functions in isolation:
- Dog creation with valid data
- Input validation (missing fields, invalid species)
- Weight parsing from various formats
- User interaction recording
- Error handling

**Run**: 
```bash
cd cdk
source .venv/bin/activate
python -m pytest tests/test_dogs_handler.py -v
```

### 2. Infrastructure Tests
**Location**: `tests/test_cdk_stack.py`

Tests CDK stack configuration:
- DynamoDB tables creation
- KMS key configuration
- Lambda function setup
- API Gateway endpoints
- IAM permissions
- Security compliance

**Run**:
```bash
python -m pytest tests/test_cdk_stack.py -v
```

### 3. Integration Tests
**Location**: `test_api.py`

Tests complete API workflows:
- End-to-end dog creation
- Data retrieval with filters
- User interactions
- Error scenarios

**Run**:
```bash
python test_api.py https://your-api-url.amazonaws.com/prod
```

### 4. Infrastructure Health Tests
**Location**: `test_runner.sh`

Tests deployed infrastructure:
- CDK synthesis validation
- DynamoDB table accessibility
- Lambda function deployment
- API endpoint availability

**Run**:
```bash
./test_runner.sh
```

## 🔍 Test Execution

### Quick Test Suite
```bash
# Run all unit tests
cd cdk
source .venv/bin/activate
python -m pytest tests/ -v

# Check infrastructure
./test_runner.sh
```

### Comprehensive Test Suite
```bash
# Install test dependencies
uv sync --group dev

# Run all tests with coverage
python -m pytest tests/ --cov=functions --cov=cdk --cov-report=html

# Check code quality
python -m black --check functions/ cdk/ tests/
python -m flake8 functions/ cdk/ tests/

# Validate CDK
cdk synth --quiet
```

## 📊 Test Coverage

### Current Coverage Areas:
- ✅ **API Endpoints**: All CRUD operations
- ✅ **Data Validation**: Required fields, species filtering
- ✅ **Security**: Encryption, IAM permissions
- ✅ **Error Handling**: Invalid inputs, system errors
- ✅ **Infrastructure**: Resource creation, configuration

### Coverage Goals:
- **Unit Tests**: >80% code coverage
- **Integration Tests**: All API endpoints
- **Security Tests**: All IAM policies, encryption
- **Performance Tests**: Response times <2s

## 🛡️ Security Testing

### Automated Security Checks:
1. **CDK Nag**: Scans for security anti-patterns
2. **IAM Policy Analysis**: Least privilege validation
3. **Encryption Verification**: Data at rest and in transit
4. **Secret Detection**: No hardcoded credentials

### Manual Security Reviews:
- API authentication mechanisms
- Data encryption implementation
- Network security configurations
- Access logging and monitoring

## 📈 Monitoring & Observability

### Structured Logging
All Lambda functions use structured logging with:
- Request IDs for tracing
- Error categorization
- Performance metrics
- User action tracking

### CloudWatch Integration
- **Logs**: Centralized log aggregation
- **Metrics**: Custom business metrics
- **Alarms**: Error rate monitoring
- **Dashboards**: Real-time visibility

### X-Ray Tracing (Ready)
Infrastructure prepared for distributed tracing:
- Lambda function instrumentation
- DynamoDB operation tracing
- API Gateway request tracking

## 🚀 Continuous Testing

### Pre-deployment Checks:
1. Unit test suite passes
2. Infrastructure tests pass
3. Security scans clean
4. Code quality standards met

### Post-deployment Validation:
1. Health check endpoints
2. Database connectivity
3. API response validation
4. Performance benchmarks

## 🔧 Test Data Management

### Test Data Strategy:
- **Unit Tests**: Mock data and services
- **Integration Tests**: Isolated test environment
- **Load Tests**: Synthetic data generation
- **Security Tests**: Sanitized production-like data

### Data Cleanup:
- Automated test data cleanup
- Isolated test environments
- No production data in tests

## 📝 Test Reporting

### Test Results:
- **Coverage Reports**: HTML and terminal output
- **Test Metrics**: Pass/fail rates, execution time
- **Security Reports**: Vulnerability assessments
- **Performance Reports**: Response time analysis

### CI/CD Integration Ready:
- JUnit XML output format
- Coverage threshold enforcement
- Automated test execution
- Failure notifications

## 🎯 Next Steps

### Immediate:
1. Run existing test suite
2. Review test coverage reports
3. Fix any failing tests
4. Validate security compliance

### Future Enhancements:
1. Add performance tests
2. Implement chaos engineering
3. Add contract testing
4. Enhance monitoring dashboards

## 📞 Troubleshooting

### Common Issues:
1. **Import Errors**: Ensure virtual environment is activated
2. **AWS Permissions**: Check IAM roles and policies
3. **Network Issues**: Verify API Gateway endpoints
4. **Data Issues**: Check DynamoDB table status

### Debug Commands:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify DynamoDB tables
aws dynamodb list-tables

# Check Lambda functions
aws lambda list-functions

# Test API endpoint
curl -v https://your-api-url/dogs
```
