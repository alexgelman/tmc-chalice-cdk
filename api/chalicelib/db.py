from typing import List
from functools import reduce

from boto3.dynamodb.conditions import Attr

from .models.item import Item


class ItemsDB:
    def list_items(self, startswith=None, address=None) -> List[Item]:
        pass

    def add_item(self, item: Item):
        pass

    def get_item(self, name) -> Item:
        pass

    def delete_item(self, name):
        pass


class DynamoItemsDB(ItemsDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_items(self, startswith=None, address=None) -> List[Item]:
        scan_params = {}
        filter_expression = None
        if startswith is not None:
            filter_expression = self._add_to_filter_expression(
                filter_expression, Attr('name').begins_with(startswith)
            )
        if address is not None:
            filter_expression = self._add_to_filter_expression(
                filter_expression, Attr('address').eq(address)
            )
        if filter_expression:
            scan_params['FilterExpression'] = filter_expression
        response = self._table.scan(**scan_params)
        items_data = response['Items']
        return [Item.Schema().load(data=item_data) for item_data in items_data]

    def add_item(self, item: Item):
        self._table.put_item(
            Item=Item.Schema().dump(item)
        )

    def get_item(self, name) -> Item:
        response = self._table.get_item(
            Key={
                'name': name,
            },
        )
        item_data = response.get('Item')
        item: Item
        if item_data is not None:
            item = Item.Schema().load(data=item_data)
        return item

    def delete_item(self, name):
        self._table.delete_item(
            Key={
                'name': name,
            }
        )

    def _add_to_filter_expression(self, expression, condition):
        if expression is None:
            return condition
        return expression & condition
