import humanfriendly

def sizeToHumanReadable(size: int) -> str:
    """Converts the size in bytes to a human readable format.
    
    Args:
        size (int): the size in bytes
        
    Returns:
        str: the human readable size
    """
    
    return humanfriendly.format_size(size)


def humanSizeToByteSize(size: str) -> int:
    """Converts the human readable size to bytes.
    
    Args:
        size (str): the human readable size
        
    Returns:
        int: the size in bytes
    """
    
    return humanfriendly.parse_size(size, binary=True) # Use binary units (1024) instead of decimal units (1000)

def humanTime(timestamp: int) -> str:
    """Converts a timestamp to a human readable time.
    
    Args:
        timestamp (int): the timestamp
        
    Returns:
        str: the human readable time
    """
    
    return humanfriendly.format_timespan(timestamp)