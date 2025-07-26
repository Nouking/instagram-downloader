"""
File Management Utilities
Handles cache cleanup and file operations
"""

import os
import glob
from pathlib import Path

class FileManager:
    """Utility class for file management operations"""

    def clear_cache_files(self, username: str):
        """Clear any existing cache files before starting fresh download"""
        print("🧹 Clearing cache files...")

        cache_patterns = [
            f"working_{username}_images.txt",
            f"{username}_images.txt",
            f"media_data_{username}.json",
            "high_quality_images.txt",
            "extracted_images.txt",
            "*.tmp"
        ]

        cleared_count = 0
        for pattern in cache_patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"  ✓ Removed: {file_path}")
                    cleared_count += 1
                except Exception as e:
                    print(f"  ⚠ Could not remove {file_path}: {e}")

        if cleared_count == 0:
            print("  ✓ No cache files found to clear")
        else:
            print(f"  ✓ Cleared {cleared_count} cache file(s)")
        print()

    def ensure_directory(self, path: str):
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)

    def get_file_count(self, directory: str, extensions: list) -> int:
        """Count files with specific extensions in directory"""
        directory_path = Path(directory)
        if not directory_path.exists():
            return 0

        count = 0
        for ext in extensions:
            count += len(list(directory_path.glob(f"*.{ext}")))
        return count
