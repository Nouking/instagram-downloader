"""
Instagram Mixed Media Downloader - Core Configuration Manager
"""

import re
from pathlib import Path

class ConfigManager:
    """Centralized configuration management"""

    def __init__(self, config_path='cookies.conf'):
        self.config_path = Path(config_path)
        self._config_data = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    self._config_data[key.strip()] = value.strip()

    @property
    def username(self) -> str:
        """Get target username"""
        username = self._config_data.get('username')
        if not username:
            raise ValueError("Username not found in configuration")
        return username

    @property
    def cookies(self) -> dict:
        """Get Instagram cookies"""
        cookie_keys = ['sessionid', 'csrftoken', 'ds_user_id', 'mid', 'ig_did', 'rur']
        cookies = {}

        for key in cookie_keys:
            value = self._config_data.get(key)
            if value and value != f'your_{key}_value':
                cookies[key] = value

        required = ['sessionid', 'csrftoken', 'ds_user_id']
        missing = [k for k in required if k not in cookies]
        if missing:
            raise ValueError(f"Missing required cookies: {', '.join(missing)}")

        return cookies

    @property
    def video_settings(self) -> dict:
        """Get video download settings"""
        return {
            'download_videos': self._config_data.get('download_videos', 'true').lower() == 'true',
            'download_images': self._config_data.get('download_images', 'true').lower() == 'true',
            'video_quality': self._config_data.get('video_quality', 'highest'),
            'max_video_size_mb': int(self._config_data.get('max_video_size_mb', 50))
        }

    def get(self, key: str, default=None):
        """Get any configuration value"""
        return self._config_data.get(key, default)
