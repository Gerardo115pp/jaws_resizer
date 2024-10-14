import pathlib
import os

def PathExists(path: str) -> bool:
    return os.path.exists(path)

def IsDirectory(path: str) -> bool:
    path: pathlib.Path = pathlib.Path(path)

    is_directory: bool = path.exists()
    
    if not is_directory:
        return False
    
    is_directory = path.is_dir()
    
    return is_directory
    