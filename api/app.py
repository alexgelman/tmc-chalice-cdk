import os

import json
import boto3
from chalice import Chalice
from chalice import Response
from chalice import BadRequestError
from chalice import NotFoundError

from typing import List
from marshmallow import ValidationError

from chalicelib import db
from chalicelib.models.item import Item

app = Chalice(app_name='items-manager')

_ITEMS_DB = None


def get_items_db() -> db.ItemsDB:
    global _ITEMS_DB
    if _ITEMS_DB is None:
        _ITEMS_DB = db.DynamoItemsDB(
            boto3.resource('dynamodb').Table(
                os.environ['ACCOUNTS_TABLE_NAME']))
    return _ITEMS_DB


@app.route('/items/{name}')
def get_item(name):
    item: Item = get_items_db().get_item(name)
    if item is None:
        raise NotFoundError(f'Item: ({name}) not found')
    # Return the item without the secret field
    return Item.Schema(exclude=["secret"]).dumps(obj=item)


@app.route('/secrets/{name}', methods=['GET'])
def get_secret(name: str):
    item: Item = get_items_db().get_item(name)
    if item is None:
        raise NotFoundError(f'Item: ({name}) not found')
    # Return only the secret field from the item
    return Item.Schema(only=["secret"]).dumps(obj=item)


@app.route('/items', methods=['POST'])
def create_item():
    event = app.current_request.json_body
    try:
        input_item: Item = Item.Schema().load(data=event)
    except ValidationError as err:
        print(err.messages)
        raise BadRequestError(err.messages)
    get_items_db().add_item(input_item)
    return Response(body="", status_code=201)


@app.route('/items/{name}', methods=['DELETE'])
def delete_item(name):
    get_items_db().delete_item(name)
    return Response(body="", status_code=204)


@app.route('/items', methods=['GET'])
def list_items():
    params = {}
    if app.current_request.query_params:
        params = _extract_items_list_params(app.current_request.query_params)
    items: List[Item] = get_items_db().list_items(**params)
    json_items = [Item.Schema(exclude=["secret"]).dump(item) for item in items]
    return json_items


def _extract_items_list_params(query_params):
    valid_query_params = ['startswith', 'address']
    return {
        k.replace('-', '_'): v
        for k, v in query_params.items() if k in valid_query_params
    }
