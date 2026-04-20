import json
import os
import urllib.request

import boto3
from botocore.exceptions import ClientError


def client(service_name: str):
    return boto3.client(
        service_name,
        endpoint_url=os.environ["AWS_ENDPOINT_URL"],
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )


def ensure_bucket(s3_client, bucket_name: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)


def ensure_queue(sqs_client, queue_name: str):
    try:
        sqs_client.get_queue_url(QueueName=queue_name)
    except ClientError:
        sqs_client.create_queue(QueueName=queue_name)


def ensure_table(ddb_client, table_name: str):
    existing_tables = set(ddb_client.list_tables().get("TableNames", []))
    if table_name in existing_tables:
        return

    ddb_client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def write_bootstrap_marker(s3_client, bucket_name: str):
    payload = {
        "project": "medium-sdd",
        "env": "local",
        "endpoint": os.environ["AWS_ENDPOINT_URL"],
        "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    }
    s3_client.put_object(
        Bucket=bucket_name,
        Key="bootstrap/health.json",
        Body=json.dumps(payload, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def wait_for_gateway():
    health_url = "http://localhost:4566/_ministack/health"
    urllib.request.urlopen(health_url, timeout=5).read()


def main():
    wait_for_gateway()

    s3_client = client("s3")
    sqs_client = client("sqs")
    ddb_client = client("dynamodb")
    sts_client = client("sts")

    bucket_name = "medium-sdd-local"
    queue_name = "medium-sdd-events"
    table_name = "medium-sdd-config"

    ensure_bucket(s3_client, bucket_name)
    ensure_queue(sqs_client, queue_name)
    ensure_table(ddb_client, table_name)
    write_bootstrap_marker(s3_client, bucket_name)

    ddb_client.put_item(
        TableName=table_name,
        Item={
            "id": {"S": "bootstrap"},
            "project": {"S": "medium-sdd"},
            "status": {"S": "ready"},
        },
    )

    identity = sts_client.get_caller_identity()
    print(
        "MiniStack bootstrap complete:",
        {
            "bucket": bucket_name,
            "queue": queue_name,
            "table": table_name,
            "account": identity.get("Account"),
        },
    )


if __name__ == "__main__":
    main()
