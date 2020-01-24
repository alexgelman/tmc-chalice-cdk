import os
from os import path

from aws_cdk import aws_dynamodb, aws_iam, core
from aws_cdk.core import Construct
from aws_cdk.aws_dynamodb import Attribute, AttributeType, Table
from aws_cdk.aws_iam import Role, ServicePrincipal
from cdk_chalice import Chalice


class ItemsManagerStack(core.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        item_table = Table(self, 'ItemTable',
            partition_key=Attribute(
                name='name',
                type=AttributeType.STRING))

        principal = 'lambda.amazonaws.com'
        api_role = Role(self,
            'ApiRole',
            assumed_by=ServicePrincipal(principal))
        item_table.grant_read_write_data(api_role)

        chalice_config = {
            'lambda_functions': {
                'api_handler': {
                    'manage_iam_role': False,
                    'iam_role_arn': api_role.role_arn,
                    'environment_variables': {
                        'TABLE_NAME':
                            item_table.table_name,
                    }}}}

        self.chalice_app = Chalice(self,
            'ItemsManagerApi',
            source_dir='./api',
            stage_config=chalice_config)
