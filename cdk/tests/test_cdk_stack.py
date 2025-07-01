import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest
from cdk.cdk_stack import CdkStack

class TestCdkStack:
    """Test suite for CDK stack infrastructure"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = core.App()
        self.stack = CdkStack(self.app, "test-stack")
        self.template = assertions.Template.from_stack(self.stack)

    def test_dynamodb_tables_created(self):
        """Test that DynamoDB tables are created with correct configuration"""
        # Test dogs table
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "pupper-dogs",
            "BillingMode": "PAY_PER_REQUEST",
            "PointInTimeRecoverySpecification": {
                "PointInTimeRecoveryEnabled": True
            }
        })
        
        # Test interactions table
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "pupper-user-interactions",
            "BillingMode": "PAY_PER_REQUEST"
        })

    def test_kms_key_created(self):
        """Test that KMS key is created for encryption"""
        self.template.has_resource_properties("AWS::KMS::Key", {
            "Description": "KMS key for encrypting dog names in Pupper app",
            "EnableKeyRotation": True
        })

    def test_lambda_function_created(self):
        """Test that Lambda function is created with correct configuration"""
        self.template.has_resource_properties("AWS::Lambda::Function", {
            "Runtime": "python3.12",
            "Handler": "dogs.handler",
            "Timeout": 30
        })

    def test_api_gateway_created(self):
        """Test that API Gateway is created"""
        self.template.has_resource_properties("AWS::ApiGateway::RestApi", {
            "Name": "Pupper API",
            "Description": "API for Pupper dog adoption application"
        })

    def test_global_secondary_indexes(self):
        """Test that GSIs are created correctly"""
        # Check for StateIndex
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "StateIndex",
                    "KeySchema": [
                        {"AttributeName": "state", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"}
                    ]
                }
            ]
        })

    def test_iam_permissions(self):
        """Test that Lambda has proper IAM permissions"""
        # Test DynamoDB permissions
        self.template.has_resource_properties("AWS::IAM::Policy", {
            "PolicyDocument": {
                "Statement": assertions.Match.array_with([
                    {
                        "Effect": "Allow",
                        "Action": [
                            "dynamodb:BatchGetItem",
                            "dynamodb:BatchWriteItem",
                            "dynamodb:ConditionCheckItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:DescribeTable",
                            "dynamodb:GetItem",
                            "dynamodb:GetRecords",
                            "dynamodb:GetShardIterator",
                            "dynamodb:PutItem",
                            "dynamodb:Query",
                            "dynamodb:Scan",
                            "dynamodb:UpdateItem"
                        ]
                    }
                ])
            }
        })
        
        # Test KMS permissions
        self.template.has_resource_properties("AWS::IAM::Policy", {
            "PolicyDocument": {
                "Statement": assertions.Match.array_with([
                    {
                        "Effect": "Allow",
                        "Action": [
                            "kms:Decrypt",
                            "kms:DescribeKey",
                            "kms:Encrypt",
                            "kms:GenerateDataKey*",
                            "kms:ReEncrypt*"
                        ]
                    }
                ])
            }
        })

    def test_api_endpoints_created(self):
        """Test that all required API endpoints are created"""
        # Test that we have the correct number of API Gateway methods
        methods = self.template.find_resources("AWS::ApiGateway::Method")
        
        # Should have methods for: GET /dogs, POST /dogs, GET /dogs/{id}, 
        # PUT /dogs/{id}, DELETE /dogs/{id}, POST /interactions, GET /interactions
        # Plus OPTIONS methods for CORS
        assert len(methods) >= 7

    def test_environment_variables(self):
        """Test that Lambda has correct environment variables"""
        self.template.has_resource_properties("AWS::Lambda::Function", {
            "Environment": {
                "Variables": {
                    "DOGS_TABLE_NAME": assertions.Match.any_value(),
                    "INTERACTIONS_TABLE_NAME": assertions.Match.any_value(),
                    "KMS_KEY_ID": assertions.Match.any_value()
                }
            }
        })

    def test_table_encryption(self):
        """Test that tables are encrypted with KMS"""
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "SSESpecification": {
                "SSEEnabled": True,
                "SSEType": "KMS"
            }
        })

    def test_cors_configuration(self):
        """Test that CORS is properly configured"""
        # Check for OPTIONS methods (CORS preflight)
        options_methods = [
            resource for resource_id, resource in 
            self.template.find_resources("AWS::ApiGateway::Method").items()
            if resource.get("Properties", {}).get("HttpMethod") == "OPTIONS"
        ]
        
        assert len(options_methods) > 0, "No OPTIONS methods found for CORS"

    def test_resource_naming_consistency(self):
        """Test that resources follow consistent naming patterns"""
        # Check that table names are consistent
        dogs_table = self.template.find_resources("AWS::DynamoDB::Table", {
            "TableName": "pupper-dogs"
        })
        interactions_table = self.template.find_resources("AWS::DynamoDB::Table", {
            "TableName": "pupper-user-interactions"
        })
        
        assert len(dogs_table) == 1, "Dogs table not found or duplicated"
        assert len(interactions_table) == 1, "Interactions table not found or duplicated"

class TestStackSecurity:
    """Security-focused tests for the CDK stack"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = core.App()
        self.stack = CdkStack(self.app, "test-stack")
        self.template = assertions.Template.from_stack(self.stack)

    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded in the template"""
        template_json = self.template.to_json()
        template_str = str(template_json).lower()
        
        # Check for common secret patterns
        forbidden_patterns = [
            'password',
            'secret',
            'apikey',
            'accesskey',
            'privatekey'
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in template_str, f"Potential hardcoded secret found: {pattern}"

    def test_encryption_at_rest(self):
        """Test that data is encrypted at rest"""
        # DynamoDB tables should be encrypted
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "SSESpecification": {
                "SSEEnabled": True
            }
        })

    def test_least_privilege_iam(self):
        """Test that IAM policies follow least privilege principle"""
        # Lambda should not have admin permissions
        policies = self.template.find_resources("AWS::IAM::Policy")
        
        for policy_id, policy in policies.items():
            statements = policy.get("Properties", {}).get("PolicyDocument", {}).get("Statement", [])
            for statement in statements:
                actions = statement.get("Action", [])
                if isinstance(actions, list):
                    assert "*" not in actions, f"Overly permissive IAM policy found in {policy_id}"

if __name__ == '__main__':
    pytest.main([__file__])
