from .file_sniffers import detectContentTypeByFilename as __detectContentTypeByFilename
from .file_sniffers import sniffContentType as __sniffContentType

SUPPORTED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
}

MIME_TO_EXTENSION = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
}

def isFileSupported(file_path: str, use_robust: bool=True) -> bool:
    """Returns True if the file is a supported mime type.

    args:
        file_path (str): the path to the file
        use_robust (bool): if extension detection fails, try content sniffing which requires reading the file which is slower.
    
    returns:
        bool: is the file supported
    """

    content_type = __detectContentTypeByFilename(file_path)
    
    if not content_type and not use_robust:
        return False

    if not content_type:
        sniffed_content_type = __sniffContentType(file_path)
        if not sniffed_content_type:
            return False

        content_type = sniffed_content_type
    
    return content_type in SUPPORTED_MIME_TYPES
    
def getExtensionFromMime(mime_type: str) -> str:
    """Returns the file extension from the mime type.

    args:
        mime_type (str): the mime type
    
    returns:
        str: the file extension
    """

    return MIME_TO_EXTENSION.get(mime_type, 'bin') 