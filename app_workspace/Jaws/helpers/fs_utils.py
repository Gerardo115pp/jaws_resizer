import pathlib
import os

def DirectorySize(root_path: str) -> int:
    """Returns the size of the directory and it's contents in bytes.
    """
    directory_size: int = 0

    directory_path: pathlib.Path = pathlib.Path(root_path)
    
    if not directory_path.exists():
        return directory_size
   
    directory_size = sum(f.stat().st_size for f in directory_path.glob('**/*') if f.is_file()) 

    return directory_size

def GetFileExtension(path: str) -> str:
    """Returns the file extension of the file.
    """
    
    file_path: pathlib.Path = pathlib.Path(path)
    
    return file_path.suffix

def GetUniqueFilename(filepath: str) -> str:
    """Returns a unique filename by appending a number to the filename.
    """
    file: pathlib.Path = pathlib.Path(filepath)
    
    if not file.exists():
        return filepath

    file_stem: str = file.stem
    file_suffix: str = file.suffix
    
    unique_fragment_prefix: str = "chew_"

    unique_counter: int = 1
    while file.exists():
        filename = f"{file_stem}.{unique_fragment_prefix}{unique_counter}{file_suffix}"
        filename = os.path.join(file.parent, filename)
        file = pathlib.Path(filename)
        unique_counter += 1
    
    return filename

def IsDirectory(path: str) -> bool:
    path: pathlib.Path = pathlib.Path(path)

    is_directory: bool = path.exists()
    
    if not is_directory:
        return False
    
    is_directory = path.is_dir()
    
    return is_directory

def PathExists(path: str) -> bool:
    return os.path.exists(path)

def ReplaceFileExtension(filepath: str, ext: str) -> str:
    """Replaces the file extension of the file.
    """
    if not ext.startswith('.'):
        ext = f".{ext}"
    
    file_path: pathlib.Path = pathlib.Path(filepath)
    
    suffixed_file_path = file_path.with_suffix(ext)

    return str(suffixed_file_path)
    
