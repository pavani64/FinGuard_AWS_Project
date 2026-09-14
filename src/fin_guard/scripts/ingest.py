"""
AWS S3 Dataset Ingestion Pipeline
---------------------------------

This script downloads a financial markets dataset from Kaggle and uploads
the configured source files to the landing layer of an Amazon S3 data lake.

Pipeline flow:
    Kaggle Dataset
        ↓
    Download dataset locally
        ↓
    Discover configured source files
        ↓
    Generate partitioned S3 object keys
        ↓
    Upload files to the S3 landing layer

The FILE_MAPPINGS configuration maps each source dataset file to its
corresponding S3 landing-layer prefix. This allows the same ingestion
logic to be reused for different Kaggle datasets by changing only the
dataset handle and file mappings.

Example S3 structure:

    s3://finguard-data/
        landing/
            global_financial_markets_2000_Now/
                ingestion_date=YYYY-MM-DD/
                    global_financial_markets_2000_Now.csv

The landing layer preserves the source data before downstream
transformation into Bronze, Silver, and Gold layers.
"""

from fin_guard.ingestion.kaggle_client import download_dataset
from fin_guard.ingestion.file_discovery import discover_files
from fin_guard.ingestion.s3_uploader import upload_file , build_s3_key , list_objects_s3

DATASET_HANDLE = "computingvictor/transactions-fraud-datasets"
BUCKET_NAME = 'finguard-data'

def ingest():
    dataset_path = download_dataset(DATASET_HANDLE)

    File_Mappings ={
    'cards_data.csv' :'landing/cards_data' ,
    'mcc_codes.json' : 'landing/mcc_codes' ,
    'train_fraud_labels.json' : 'landing/train_fraud_labels' ,
    'transactions_data.csv' : 'landing/transactions_data' ,
    'users_data.csv' :'landing/users_data' 
    #  'global_financial_markets_2000_Now.csv' :'landing/global_financial_markets_2000_Now'
     }
    dataset_files = discover_files(dataset_path, File_Mappings)
    
    for dataset_file in dataset_files:
          print(f"File: {dataset_file.file_path.name}")
          print(f"S3 destination: {dataset_file.s3_prefix}")
          print(f's3 path : {build_s3_key(dataset_file)}')
          upload_file(
            dataset_file=dataset_file,
            bucket_name=BUCKET_NAME
        )

    list_objects_s3('finguard-data')
    
   
if __name__ == "__main__":
    ingest()
    