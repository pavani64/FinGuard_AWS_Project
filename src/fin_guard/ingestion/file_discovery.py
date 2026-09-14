"""
Dataset File Discovery
----------------------

This module provides utilities for discovering dataset files that are
configured for ingestion.

It scans a downloaded dataset directory and matches files against a
configuration mapping. Each matched file is represented as a DatasetFile
object containing the local source path and its corresponding Amazon S3
destination prefix.

This keeps file discovery independent of dataset-specific configuration,
allowing the same ingestion logic to be reused across different datasets.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass 
class DatasetFile:
    file_path:str
    s3_prefix :str


def discover_files(dataset_path:Path, file_mappings:Dict) ->list[DatasetFile] :
     discovered_file =[]
     for file in dataset_path.iterdir():
        if file.name in file_mappings:
            dataset_file =DatasetFile(
                file_path = file ,
                s3_prefix = file_mappings[file.name]
            )
        discovered_file.append(dataset_file)
     return discovered_file

