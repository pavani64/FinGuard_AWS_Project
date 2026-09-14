"""
Amazon S3 File Upload
---------------------

This module provides utilities for uploading discovered dataset files
to the Landing layer of the FinGuard AWS data lake.

For each DatasetFile, the module:

    1. Generates a date-partitioned S3 object key.
    2. Creates an Amazon S3 client using boto3.
    3. Uploads the local source file to the configured S3 bucket.

Files are stored using an ingestion-date partitioning convention:

    <s3_prefix>/
        ingestion_date=YYYY-MM-DD/
            <source_filename>

Example:

    landing/global_financial_markets_2000_Now/
        ingestion_date=2026-09-14/
            global_financial_markets_2000_Now.csv

This structure preserves the original source file while organizing
ingestion runs by date, supporting traceability, historical processing,
and downstream data lake transformations.
"""
from datetime import date
import boto3

from fin_guard.ingestion.file_discovery import DatasetFile, discover_files

s3 = boto3.client("s3")
def build_s3_key(datasetFile: DatasetFile) ->str:
    ingestion_date = date.today().isoformat()
    return (
        f'{datasetFile.s3_prefix}/'
        f'ingestion_date={ingestion_date}/'
        f'{datasetFile.file_path.name}'
    )

def upload_file(dataset_file: DatasetFile,
    bucket_name: str) -> None:
    
      
    s3_key = build_s3_key(dataset_file)
    s3.upload_file(
        str(dataset_file.file_path),
        bucket_name,
        s3_key
    )
    
    print(
        f"Uploaded {dataset_file.file_path.name} "
        f"to s3://{bucket_name}/{s3_key}"
    )

def list_objects_s3(bucketname) ->None:
     response = s3.list_objects_v2(Bucket=bucketname)
     for obj in response.get("Contents", []):
      print(obj['Key'])