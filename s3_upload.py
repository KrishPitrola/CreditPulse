"""
s3_upload.py
------------
Uploads the raw CSVs to an S3 bucket -- this becomes the pipeline's
"raw zone", the standard first stop for data before any processing
(a pattern called a data lake). Real pipelines almost always land
raw data in cloud storage like this before touching it.

PREREQUISITES (you do these yourself, see instructions below):
    1. AWS account created
    2. AWS CLI installed and configured (`aws configure`)
    3. An S3 bucket created (or let this script create one)
    4. `pip install boto3`

Run with:
    python s3_upload.py
"""

import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = "creditpulse-raw-1"  # S3 bucket names must be globally unique
REGION = "ap-south-1"  # Mumbai region -- makes sense given the project's theme

FILES_TO_UPLOAD = [
    ("data/customers.csv", "raw/customers.csv"),
    ("data/loans.csv", "raw/loans.csv"),
    ("data/repayments.csv", "raw/repayments.csv"),
]


def create_bucket_if_not_exists(s3_client, bucket_name, region):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except ClientError:
        print(f"Creating bucket '{bucket_name}' in {region}...")
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        print("Bucket created.")


def main():
    s3 = boto3.client("s3", region_name=REGION)

    create_bucket_if_not_exists(s3, BUCKET_NAME, REGION)

    for local_path, s3_key in FILES_TO_UPLOAD:
        print(f"Uploading {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
        s3.upload_file(local_path, BUCKET_NAME, s3_key)

    print("\nDone. Verify in the AWS Console under S3 -> your bucket -> raw/")


if __name__ == "__main__":
    main()
