import os
import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2"),
)

def generate_presigned_url(filename: str, expiration: int = 3600):
    bucket = os.getenv("S3_BUCKET_NAME")
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": filename},
        ExpiresIn=expiration,
    )
