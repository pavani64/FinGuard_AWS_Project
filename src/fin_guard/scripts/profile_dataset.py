"""
S3 Landing Data Profiler
------------------------

Profiles datasets stored in the S3 Landing layer.

For every supported data file found under the Landing prefix,
the profiler reports:

    - Sample records
    - Column names
    - Data types
    - Null values
    - Duplicate records

The profiler uses boto3 for S3 access and Pandas for
dataset-level inspection.
"""

import pandas as pd
import boto3
import json 
BUCKET_NAME="finguard-data"
LANDING_PREFIX = "landing/"

def list_landing_files(bucket_name:str, prefix:str) -> list[str]:
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    files =[]
    for page in pages:
        for obj in page.get("Contents", []):
            key = obj['Key']
            if key.endswith((".csv", ".json")):
                files.append(key)

    return files
def read_s3_file(bucket_name: str, s3_key: str) -> pd.DataFrame:
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=bucket_name,
        Key=s3_key
    )
    body = response["Body"]
    if s3_key.endswith('.csv'):
       return  pd.read_csv(body)
    # JSON files can have different structures, so convert each structure
    # appropriately into a DataFrame for consistent downstream profiling.
    if s3_key.endswith('.json'):
        data = json.load(body)
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):

            # Flat key-value JSON such as:
            #
            # {
            #     "5812": "Restaurants",
            #     "5912": "Pharmacies"
            # }
            #
            # Convert into:
            #
            # key     value
            # 5812    Restaurants
            # 5912    Pharmacies

         if all(not isinstance(value, (dict, list))
                for value in data.values()):
                return pd.DataFrame(
                    data.items(),
                    columns=["key", "value"]
                )

            # Nested dictionary with one outer key such as:
            #
            # {
            #     "target": {
            #         "12345": "No",
            #         "67890": "Yes"
            #     }
            # }
            #
            # Convert into:
            #
            # key      target
            # 12345    No
            # 67890    Yes

         if len(data) == 1:

                outer_key = next(iter(data))
                inner_data = data[outer_key]

                if isinstance(inner_data, dict):

                    return pd.DataFrame(
                        inner_data.items(),
                        columns=["key", outer_key]
                    )

        raise ValueError(
            f"Unsupported JSON structure: {s3_key}"
        )
    raise ValueError(
        f"Unsupported file type: {s3_key}"
    )
    
def profile_dataframe(df :pd.DataFrame, s3_key: str) ->None:
    """
    Print basic profiling information for a dataset.
    """

    print("\n")
    print("=" * 80)
    print(f"FILE: {s3_key}")
    print("=" * 80)

    print("\n--- SAMPLE RECORDS ---")
    print(df.head())

    print("\n--- COLUMN NAMES ---")
    print(df.columns.tolist())

    print("\n--- Data Types  ---")
    print(df.dtypes)

    print("\n--- Null Checks  ---")
    print(df.isnull().sum())

    print("\n--- Duplicate checks  ---")
    duplicated_count = df.duplicated().sum()
    print(f'number of duplicates : {duplicated_count}')

files =list_landing_files (BUCKET_NAME ,prefix=LANDING_PREFIX)
print(f"Found {len(files)} files under s3://{BUCKET_NAME}/{LANDING_PREFIX}")
for file in files:
    print(file)
    try:
     df =read_s3_file(BUCKET_NAME,file)
     profile_dataframe(df,file)
    except Exception as e:
        print(f"Failed to profile {file}: {e}")

        