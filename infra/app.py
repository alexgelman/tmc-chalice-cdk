#!/usr/bin/env python3

from aws_cdk import core

from stacks.items_manager_stack import ItemsManagerStack


app = core.App()
ItemsManagerStack(app, "infra")

app.synth()
