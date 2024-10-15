import mimetypes
import magic as libmagic

def detectContentTypeByFilename(filename) -> str | None:
    """Returns a guess of the file's mime type based on the filename extension. If it can't be determined, None is returned.
    Keep in mind this is only reliable if you don't expect incorrect or malicious filenames. It will only return null if the file extension
    is not recognized.

    Args:
        filename (str): the filename to identify

    Returns:
        str: the mime type with the format 'type/subtype' or None
    """
    mime_type, _ = mimetypes.guess_type(filename, strict=False)

    return mime_type

def sniffContentType(filename: str) -> str | None:
    """Returns the mime type of the file based on it's content. If it can't be determined, None is returned.

    Args:
        filename (str): the filename to identify

    Returns:
        str: the mime type with the format 'type/subtype' or None
    """
    mime = libmagic.Magic(mime=True)
    mime_type = mime.from_file(filename)
    
    return mime_type

def sniffContentTypeByBytes(filename: str, buffer_size: int = 512) -> str | None:
    """Returns the mime type of the file based on the first bytes of the file. If it can't be determined, None is returned.

    Args:
        filename (str): the filename to identify
        buffer_size (int): the number of bytes to read from the file

    Returns:
        str: the mime type with the format 'type/subtype' or None
    """
    mime = libmagic.Magic(mime=True)
    
    buffer:bytes
    
    with open(filename, 'rb') as file:
        buffer = file.read(buffer_size)
        
    mime_type = mime.from_buffer(buffer)
    
    return mime_type