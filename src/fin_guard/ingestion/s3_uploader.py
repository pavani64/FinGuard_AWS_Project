from datetime import date
import boto3

from fin_guard.ingestion.file_discovery import DatasetFile, discover_files

def build_s3_key(datasetFile: DatasetFile) ->str:
    ingestion_date = date.today().isoformat()
    return (
        f'{datasetFile.s3_prefix}/'
        f'ingestion_date={ingestion_date}/'
        f'{datasetFile.file_path.name}'
    )

def upload_file(dataset_file: DatasetFile,
    bucket_name: str) -> None:
    s3 = boto3.client("s3")

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
