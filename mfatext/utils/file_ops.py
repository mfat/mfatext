"""File operations utilities.

This module provides functions for loading and saving files with proper
encoding detection and error handling.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def detect_encoding(file_path: Path) -> Tuple[str, bytes]:
    """Detect the encoding of a file.
    
    Attempts to decode as UTF-8 first, then falls back to latin-1,
    and finally uses UTF-8 with error replacement.
    
    Args:
        file_path: Path to the file to detect encoding for
        
    Returns:
        Tuple of (encoding_name, file_content_bytes)
    """
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Try UTF-8 first
    try:
        content.decode('utf-8')
        return 'utf-8', content
    except UnicodeDecodeError:
        pass
    
    # Try latin-1 (covers all byte values)
    try:
        content.decode('latin-1')
        return 'latin-1', content
    except UnicodeDecodeError:
        pass
    
    # Fallback to UTF-8 with error replacement
    return 'utf-8', content


def load_file(file_path: Path) -> str:
    """Load a text file with automatic encoding detection.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        File contents as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If the file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    encoding, content = detect_encoding(file_path)
    
    try:
        text = content.decode(encoding) if encoding != 'utf-8' else content.decode('utf-8', errors='replace')
        logger.debug(f"Loaded file {file_path} with encoding {encoding}")
        return text
    except Exception as e:
        logger.error(f"Failed to decode file {file_path}: {e}")
        raise IOError(f"Failed to decode file: {e}") from e


def save_file(file_path: Path, content: str, encoding: str = 'utf-8') -> None:
    """Save text content to a file.
    
    Args:
        file_path: Path where to save the file
        content: Text content to save
        encoding: Encoding to use (default: utf-8)
        
    Raises:
        IOError: If the file cannot be written
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        logger.debug(f"Saved file {file_path} with encoding {encoding}")
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise IOError(f"Failed to save file: {e}") from e

