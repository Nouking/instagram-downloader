"""
Universal Media Downloader - Refactored
Handles downloading of both images and videos with progress tracking
"""

import os
import requests
import time
import random
from urllib.parse import urlparse
from tqdm import tqdm
from pathlib import Path

class MediaDownloader:
    """Universal downloader for images and videos"""

    def __init__(self, download_folder: str, video_settings: dict = None):
        self.download_folder = Path(download_folder)
        self.video_settings = video_settings or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.download_folder.mkdir(parents=True, exist_ok=True)

    def generate_filename(self, media_item: dict) -> str:
        """Generate descriptive filename for media item"""
        post_index = media_item.get('post_index', 1)
        media_index = media_item.get('media_index', 1)
        media_type = media_item.get('type', 'unknown')

        base = f"post_{post_index:03d}"

        if media_type == 'image':
            suffix = f"_img_{media_index:02d}" if media_index > 1 else "_img"
            return f"{base}{suffix}.jpg"
        elif media_type == 'video':
            suffix = f"_video_{media_index:02d}" if media_index > 1 else "_video"
            return f"{base}{suffix}.mp4"

        return f"{base}_unknown.bin"

    def _handle_filename_collision(self, filepath: Path) -> Path:
        """Handle duplicate filenames gracefully"""
        if not filepath.exists():
            return filepath

        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1

        while filepath.with_name(f"{stem}_{counter}{suffix}").exists():
            counter += 1

        return filepath.with_name(f"{stem}_{counter}{suffix}")

    def _check_video_size_limit(self, total_size: int) -> bool:
        """Check if video exceeds size limit"""
        max_size_bytes = self.video_settings.get('max_video_size_mb', 50) * 1024 * 1024
        if total_size > max_size_bytes:
            size_mb = total_size / 1024 / 1024
            limit_mb = max_size_bytes / 1024 / 1024
            print(f"Skipping large video: {size_mb:.1f}MB > {limit_mb}MB")
            return False
        return True

    def download_with_progress(self, url: str, filepath: Path, file_type: str = 'image') -> bool:
        """Download file with progress tracking"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            # Check video size limit
            if file_type == 'video' and total_size > 0:
                if not self._check_video_size_limit(total_size):
                    return False

            # Handle filename collision
            filepath = self._handle_filename_collision(filepath)

            with open(filepath, 'wb') as f:
                if total_size > 0:
                    with tqdm(
                        desc=f"Downloading {file_type}",
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # No content-length header
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            return True

        except Exception as e:
            print(f"Download failed: {e}")
            if filepath.exists():
                filepath.unlink()  # Clean up partial file
            return False

    def download_media_item(self, media_item: dict) -> bool:
        """Download single media item"""
        filename = self.generate_filename(media_item)
        filepath = self.download_folder / filename
        file_type = media_item.get('type', 'unknown')
        url = media_item.get('url')

        if not url:
            print(f"No URL found for {filename}")
            return False

        return self.download_with_progress(url, filepath, file_type)

    def download_with_retry(self, media_item: dict, max_retries: int = 3) -> bool:
        """Download with retry logic"""
        for attempt in range(max_retries):
            if self.download_media_item(media_item):
                return True
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1}/{max_retries} in 2 seconds...")
                time.sleep(2)
        return False

    def download_all_media(self, media_data: dict) -> dict:
        """Download all media items with progress reporting"""
        images = media_data.get('images', [])
        videos = media_data.get('videos', [])
        total_items = len(images) + len(videos)

        if total_items == 0:
            print("No media items to download")
            return {'images': 0, 'videos': 0, 'failed': 0}

        print(f"Starting download of {len(images)} images and {len(videos)} videos")
        print(f"Download folder: {self.download_folder}")

        successful_images = 0
        successful_videos = 0
        failed = 0

        # Download images
        for i, image_item in enumerate(images, 1):
            print(f"\nDownloading image {i}/{len(images)}")
            if self.download_with_retry(image_item):
                successful_images += 1
            else:
                failed += 1
            time.sleep(random.uniform(0.5, 1.0))

        # Download videos
        for i, video_item in enumerate(videos, 1):
            print(f"\nDownloading video {i}/{len(videos)}")
            if self.download_with_retry(video_item):
                successful_videos += 1
            else:
                failed += 1
            time.sleep(random.uniform(1.0, 2.0))

        results = {
            'images': successful_images,
            'videos': successful_videos,
            'failed': failed
        }

        print(f"\n=== Download Complete ===")
        print(f"Successfully downloaded: {successful_images} images, {successful_videos} videos")
        print(f"Failed downloads: {failed}")

        return results
