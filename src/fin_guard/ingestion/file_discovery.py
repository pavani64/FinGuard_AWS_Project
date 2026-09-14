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

