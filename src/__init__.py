"""
Instagram Mixed Media Downloader Package
Clean, refactored version with organized structure
"""

# Package information
__version__ = "2.0.0"
__author__ = "Instagram Downloader Team"
__description__ = "Download images and videos from Instagram profiles"

# Main imports for easy access
from .core.config import ConfigManager
from .extractors.graphql_extractor import InstagramGraphQLExtractor
from .downloaders.media_downloader import MediaDownloader
from .utils.file_manager import FileManager

__all__ = [
    'ConfigManager',
    'InstagramGraphQLExtractor',
    'MediaDownloader',
    'FileManager'
]
