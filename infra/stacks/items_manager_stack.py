import os

from aws_cdk import aws_dynamodb, aws_iam, core
from cdk_chalice import Chalice


class ItemsManagerStack(core.Stack):
    
    _API_HANDLER_LAMBDA_MEMORY_SIZE = 128
    _API_HANDLER_LAMBDA_TIMEOUT = 10

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.items_table = aws_dynamodb.Table(self, f"{id}ItemsTable",
            partition_key=aws_dynamodb.Attribute(
                name="name",
                type=aws_dynamodb.AttributeType.STRING),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY)
        
        lambda_service_principal = aws_iam.ServicePrincipal('lambda.amazonaws.com')
        self.api_handler_iam_role = aws_iam.Role(self, 'ItemsManagerApiHandlerLambdaRole', assumed_by=lambda_service_principal)
        self.items_table.grant_read_write_data(self.api_handler_iam_role)

        api_source_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'api')

        chalice_stage_config = self._create_chalice_stage_config()
        self.chalice_app = Chalice(self, 'ItemsManagerApi', source_dir=api_source_dir, stage_config=chalice_stage_config)

    def _create_chalice_stage_config(self):
        chalice_stage_config = {
            'api_gateway_stage': 'v1',
            'lambda_functions': {
                'api_handler': {
                    'manage_iam_role': False,
                    'iam_role_arn': self.api_handler_iam_role.role_arn,
                    'environment_variables': {
                        'ACCOUNTS_TABLE_NAME': self.items_table.table_name,
                    },
                    'lambda_memory_size': ItemsManagerStack._API_HANDLER_LAMBDA_MEMORY_SIZE,
                    'lambda_timeout': ItemsManagerStack._API_HANDLER_LAMBDA_TIMEOUT
                }
            }
        }

        return chalice_stage_config
