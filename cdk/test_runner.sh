#!/bin/bash

# Pupper Application Test Runner
echo "🚀 Starting Pupper Application Test Suite"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests and track results
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "\n${YELLOW}🔍 Running: $test_name${NC}"
    echo "Command: $command"
    
    if eval "$command"; then
        echo -e "${GREEN}✅ $test_name - PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name - FAILED${NC}"
        return 1
    fi
}

# Initialize counters
PASSED=0
TOTAL=0

# Test 1: CDK Synthesis
((TOTAL++))
if run_test "CDK Synthesis" "cd /mnt/c/Users/User/pupper/cdk && source .venv/bin/activate && cdk synth --quiet"; then
    ((PASSED++))
fi

# Test 2: Python syntax check
((TOTAL++))
if run_test "Python Syntax Check" "cd /mnt/c/Users/User/pupper/cdk && python3 -m py_compile functions/dogs.py"; then
    ((PASSED++))
fi

# Test 3: API Health Check (if deployed)
if [ ! -z "$PUPPER_API_URL" ]; then
    ((TOTAL++))
    if run_test "API Health Check" "curl -s -f $PUPPER_API_URL/dogs > /dev/null"; then
        ((PASSED++))
    fi
else
    echo -e "\n${YELLOW}⚠️  Skipping API health check - PUPPER_API_URL not set${NC}"
fi

# Test 4: DynamoDB Tables Check
((TOTAL++))
if run_test "DynamoDB Tables Check" "aws dynamodb describe-table --table-name pupper-dogs --region us-east-1 > /dev/null"; then
    ((PASSED++))
fi

# Test 5: Lambda Function Check
((TOTAL++))
if run_test "Lambda Function Check" "aws lambda get-function --function-name \$(aws lambda list-functions --query 'Functions[?contains(FunctionName, \`DogsHandler\`)].FunctionName' --output text --region us-east-1) --region us-east-1 > /dev/null"; then
    ((PASSED++))
fi

# Summary
echo -e "\n${'='*60}"
echo -e "${YELLOW}📊 TEST SUMMARY${NC}"
echo -e "${'='*60}"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $((TOTAL - PASSED))${NC}"
echo -e "${YELLOW}📈 Success Rate: $(( (PASSED * 100) / TOTAL ))%${NC}"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Your infrastructure is healthy.${NC}"
    exit 0
else
    echo -e "\n${RED}💥 Some tests failed. Please check the issues above.${NC}"
    exit 1
fi
