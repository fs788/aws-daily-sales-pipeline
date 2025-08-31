from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_events as events,
    aws_events_targets as targets,
    RemovalPolicy,
    Duration,
    CfnOutput
)
from constructs import Construct


class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 buckets
        raw_bucket = s3.Bucket(self, "RawSalesDataBucket",
            bucket_name=f"raw-sales-data-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        processed_bucket = s3.Bucket(self, "ProcessedSalesDataBucket",
            bucket_name=f"processed-sales-data-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create Lambda function
        process_lambda = lambda_.Function(self, "ProcessSalesDataFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="process_data.lambda_handler",
            code=lambda_.Code.from_asset("src/lambdas"),
            timeout=Duration.seconds(30),
            environment={
                "PROCESSED_BUCKET": processed_bucket.bucket_name
            },
            memory_size=256
        )

        # Grant permissions to Lambda
        raw_bucket.grant_read(process_lambda)
        processed_bucket.grant_read_write(process_lambda)

        # Create Step Functions state machine
        process_task = tasks.LambdaInvoke(self, "ProcessSalesData",
            lambda_function=process_lambda,
            output_path="$.Payload"
        )

        success_state = sfn.Succeed(self, "Success")
        fail_state = sfn.Fail(self, "Failed")

        definition = process_task.add_catch(fail_state).next(success_state)

        state_machine = sfn.StateMachine(self, "SalesDataStateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )

        # Create EventBridge rule to trigger on S3 upload
        rule = events.Rule(self, "S3UploadRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {
                        "name": [raw_bucket.bucket_name]
                    }
                }
            )
        )

        rule.add_target(targets.SfnStateMachine(state_machine))

        # Output useful information
        CfnOutput(self, "RawBucketName", value=raw_bucket.bucket_name)
        CfnOutput(self, "ProcessedBucketName", value=processed_bucket.bucket_name)
        CfnOutput(self, "StateMachineArn", value=state_machine.state_machine_arn)
