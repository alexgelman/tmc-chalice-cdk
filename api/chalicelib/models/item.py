from typing import ClassVar, Type
from dataclasses import field
from marshmallow_dataclass import dataclass
from marshmallow import Schema, fields

import marshmallow_dataclass
import marshmallow.validate     


@dataclass
class Item:
    name: str = field(metadata={'required': True})
    address: str = field(metadata={'required': True})
    Schema: ClassVar[Type[Schema]] = Schema

    def __init__(self, name: str, address: str, secret: str):
        self.name = name
        self.address = address


ItemSchema = marshmallow_dataclass.class_schema(Item)
