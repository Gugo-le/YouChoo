#!/usr/bin/env python3
"""
Upload a FastText model file to S3 and print a presigned URL.

Usage:
  pip install boto3
  python scripts/upload_model_to_s3.py --file project/model/cc.ko.300.bin --bucket my-bucket --key models/cc.ko.300.bin --expiry 86400

The script reads AWS credentials from the environment or the usual AWS config locations.
"""
import argparse
import os
import sys
import boto3
from botocore.exceptions import ClientError


def upload_file(file_path, bucket, key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket, key)
        return True
    except ClientError as e:
        print(f"S3 upload failed: {e}")
        return False


def presign_url(bucket, key, expiry):
    s3 = boto3.client('s3')
    try:
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expiry)
        return url
    except ClientError as e:
        print(f"Presign URL generation failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Local path to model file')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--key', required=True, help='S3 object key/path')
    parser.add_argument('--expiry', type=int, default=86400, help='Presigned URL expiry in seconds (default 86400=1 day)')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Model file not found: {args.file}")
        sys.exit(2)

    print(f"Uploading {args.file} to s3://{args.bucket}/{args.key} ...")
    ok = upload_file(args.file, args.bucket, args.key)
    if not ok:
        sys.exit(1)

    print("Upload succeeded. Generating presigned URL...")
    url = presign_url(args.bucket, args.key, args.expiry)
    if url:
        print("Presigned URL:")
        print(url)
        print("Copy this URL and set it as the MODEL_URL repository secret in GitHub (short expiry is recommended).")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
