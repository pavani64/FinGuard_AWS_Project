"""
Kaggle dataset ingestion client.

Provides functionality for downloading the financial transactions and fraud
dataset from Kaggle using KaggleHub. The client abstracts Kaggle-specific
download logic and returns the local dataset location for downstream
processing.
Data set : https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data
"""

from pathlib import Path
import kagglehub



"""
    Download the configured Kaggle dataset and return its local path.
    The returned  directory is used by downstream ingestion components.

    Returns:
        Path: Local directory containing the downloaded dataset.

    Raises:
        FileNotFoundError: If the dataset directory cannot be found after
            the KaggleHub download operation.
    """

def download_dataset(dataset_handle) -> Path:
     path =kagglehub.dataset_download(dataset_handle)
    
     dataset_path =Path(path)
     
     if not dataset_path.exists():
          raise FileNotFoundError(f'dataset not found {dataset_path}')

     return dataset_path







