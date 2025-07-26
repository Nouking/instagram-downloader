"""
Instagram Mixed Media Downloader - Main Application
Clean, refactored entry point for the application
"""

import sys
from pathlib import Path
from src.core.config import ConfigManager
from src.extractors.graphql_extractor import InstagramGraphQLExtractor
from src.downloaders.media_downloader import MediaDownloader
from src.utils.file_manager import FileManager

class InstagramDownloader:
    """Main application class for Instagram media downloading"""

    def __init__(self, config_path: str = 'cookies.conf'):
        self.config = ConfigManager(config_path)
        self.file_manager = FileManager()

    def run(self) -> bool:
        """Execute the complete download process"""
        try:
            print("=== Instagram Mixed Media Downloader ===")
            print("Automated tool to download images and videos from Instagram profiles")
            print()

            # Display configuration
            username = self.config.username
            video_settings = self.config.video_settings

            print(f"Target Instagram Profile: {username}")
            if video_settings.get('download_videos', True):
                print(f"Video downloads: ENABLED (quality: {video_settings.get('video_quality', 'highest')})")
            else:
                print("Video downloads: DISABLED (images only)")
            print()

            # Clear cache files
            self.file_manager.clear_cache_files(username)

            # Step 1: Extract media URLs
            print("Step 1: Extracting media URLs (images + videos)...")
            extractor = InstagramGraphQLExtractor(self.config.cookies)

            posts = extractor.fetch_user_posts(username)
            if not posts:
                print("ERROR: No posts fetched from GraphQL")
                return False

            media_data = extractor.extract_media_from_posts(posts, video_settings)
            image_count = len(media_data.get('images', []))
            video_count = len(media_data.get('videos', []))

            if image_count == 0 and video_count == 0:
                print("ERROR: No media extracted")
                return False

            print(f"✓ Successfully extracted {image_count} images and {video_count} videos")
            print()

            # Step 2: Download all media
            print("Step 2: Downloading all media...")
            download_folder = Path("downloads") / username
            downloader = MediaDownloader(str(download_folder), video_settings)

            results = downloader.download_all_media(media_data)

            successful_images = results.get('images', 0)
            successful_videos = results.get('videos', 0)
            failed = results.get('failed', 0)

            print(f"✓ Successfully downloaded {successful_images} images and {successful_videos} videos")
            if failed > 0:
                print(f"⚠ {failed} downloads failed")

            # Final summary
            self._print_summary(username, download_folder, successful_images, successful_videos)

            return True

        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def _print_summary(self, username: str, download_folder: Path, images: int, videos: int):
        """Print final download summary"""
        print()
        print("=== Download Complete ===")

        if videos > 0:
            print(f"Complete media backup from @{username} downloaded successfully!")
            print(f"Images: {images}, Videos: {videos}")
        else:
            print(f"All images from @{username} have been downloaded successfully!")

        print(f"Location: {download_folder}")

        # Count actual files
        if download_folder.exists():
            image_files = len(list(download_folder.glob("*.jpg"))) + len(list(download_folder.glob("*.png")))
            video_files = len(list(download_folder.glob("*.mp4")))
            print(f"✓ Total files saved: {image_files} images, {video_files} videos")

def main():
    """Main entry point"""
    try:
        downloader = InstagramDownloader()
        success = downloader.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
