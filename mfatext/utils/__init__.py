"""Utility modules for the text editor."""

from mfatext.utils.xdg import get_user_data_dir, get_user_config_dir, get_user_cache_dir
from mfatext.utils.file_ops import load_file, save_file, detect_encoding

__all__ = [
    "get_user_data_dir",
    "get_user_config_dir", 
    "get_user_cache_dir",
    "load_file",
    "save_file",
    "detect_encoding",
]

