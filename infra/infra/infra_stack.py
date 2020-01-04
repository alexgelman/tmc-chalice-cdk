from aws_cdk import aws_dynamodb, core


class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        items_table = aws_dynamodb.Table(self, f"{id}-items-table",
            partition_key=aws_dynamodb.Attribute(
                name="name",
                type=aws_dynamodb.AttributeType.STRING),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST)
