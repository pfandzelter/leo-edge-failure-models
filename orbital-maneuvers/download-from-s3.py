#!/usr/bin/env python3
#
# Download archived TLE data from S3
#

import os
import sys

import boto3

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: download-from-s3.py <bucket-name> <region> <output-dir> [prefix]")
        sys.exit(1)

    bucket_name = sys.argv[1]
    region = sys.argv[2]
    output_dir = sys.argv[3]
    prefix = sys.argv[4] if len(sys.argv) > 4 else ""

    # create given output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # download all files from S3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html

    s3 = boto3.resource("s3", region_name=region)

    bucket = s3.Bucket(bucket_name)

    for obj in bucket.objects.filter(Prefix=prefix):
        print(obj.key)
        bucket.download_file(obj.key, os.path.join(output_dir, obj.key))
