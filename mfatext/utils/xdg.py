"""XDG Base Directory Standard utilities.

This module provides functions to get standard directories following the
freedesktop.org XDG Base Directory Specification.
"""

import os
from pathlib import Path
from typing import Optional


def get_user_data_dir(app_name: str = "mfatext") -> Path:
    """Get the user data directory following XDG standards.
    
    Returns $XDG_DATA_HOME/app_name or ~/.local/share/app_name
    
    Args:
        app_name: Application name for the subdirectory
        
    Returns:
        Path to the user data directory
    """
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        return Path(data_home) / app_name
    return Path.home() / ".local" / "share" / app_name


def get_user_config_dir(app_name: str = "mfatext") -> Path:
    """Get the user config directory following XDG standards.
    
    Returns $XDG_CONFIG_HOME/app_name or ~/.config/app_name
    
    Args:
        app_name: Application name for the subdirectory
        
    Returns:
        Path to the user config directory
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / app_name
    return Path.home() / ".config" / app_name


def get_user_cache_dir(app_name: str = "mfatext") -> Path:
    """Get the user cache directory following XDG standards.
    
    Returns $XDG_CACHE_HOME/app_name or ~/.cache/app_name
    
    Args:
        app_name: Application name for the subdirectory
        
    Returns:
        Path to the user cache directory
    """
    cache_home = os.environ.get("XDG_CACHE_HOME")
    if cache_home:
        return Path(cache_home) / app_name
    return Path.home() / ".cache" / app_name


def ensure_directories_exist(app_name: str = "mfatext") -> None:
    """Ensure all XDG directories exist for the application.
    
    Creates data, config, and cache directories if they don't exist.
    
    Args:
        app_name: Application name for the subdirectories
    """
    get_user_data_dir(app_name).mkdir(parents=True, exist_ok=True)
    get_user_config_dir(app_name).mkdir(parents=True, exist_ok=True)
    get_user_cache_dir(app_name).mkdir(parents=True, exist_ok=True)

