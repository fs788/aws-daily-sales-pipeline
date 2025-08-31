#!/usr/bin/env python3
import os
import aws_cdk as cdk
from infrastructure.pipeline_stack import PipelineStack

app = cdk.App()

# Use environment variables for account/region or defaults
env = cdk.Environment(
    account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
    region=os.environ.get('CDK_DEFAULT_REGION')
)

PipelineStack(app, "SalesDataPipelineStack", env=env)

app.synth()