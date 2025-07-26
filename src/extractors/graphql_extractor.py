"""
Instagram GraphQL Extractor - Refactored
Handles both image and video extraction from Instagram GraphQL API
"""

import requests
import json
import time
import random
import re

class InstagramGraphQLExtractor:
    """Enhanced GraphQL extractor for mixed media content"""

    def __init__(self, cookies: dict):
        self.session = requests.Session()
        self.cookies = cookies
        self.csrf_token = cookies.get('csrftoken', '')
        self.doc_id = "30714410208142251"
        self._setup_session()

    def _setup_session(self):
        """Configure session with headers and cookies"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
            'X-Instagram-AJAX': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/'
        })

        for name, value in self.cookies.items():
            self.session.cookies.set(name, value, domain='.instagram.com')

    def _get_fb_dtsg(self, username: str) -> str:
        """Extract fb_dtsg token from profile page"""
        try:
            response = self.session.get(f"https://www.instagram.com/{username}/")
            if response.status_code == 200:
                patterns = [
                    r'"DTSGInitialData",\[\],{"token":"([^"]+)"',
                    r'fb_dtsg[^"]*"([^"]+)"'
                ]
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        return match.group(1)
            return "NAftyF_1mkGDTmQ3T2UX_zP8C9tmpc3h3b5DguTZlumI0VqB9hHdwoQ:17843669410156967:1753514249"
        except Exception:
            return "NAftyF_1mkGDTmQ3T2UX_zP8C9tmpc3h3b5DguTZlumI0VqB9hHdwoQ:17843669410156967:1753514249"

    def detect_media_type(self, post_node: dict) -> str:
        """Detect media type from post node"""
        media_type = post_node.get('media_type', 1)
        return {1: 'image', 2: 'video', 8: 'carousel'}.get(media_type, 'unknown')

    def select_best_video_quality(self, video_versions: list, preference: str = 'highest') -> dict:
        """Select optimal video quality based on preference"""
        priority = {
            'highest': [103, 102, 101],
            'medium': [102, 103, 101],
            'lowest': [101, 102, 103]
        }

        for type_id in priority.get(preference, [103, 102, 101]):
            video = next((v for v in video_versions if v.get('type') == type_id), None)
            if video:
                return video
        return video_versions[0] if video_versions else None

    def extract_media_from_posts(self, posts: list, video_settings: dict) -> dict:
        """Extract both images and videos from posts"""
        images = []
        videos = []
        post_index = 1

        for post in posts:
            try:
                node = post.get('node', {})
                media_type = self.detect_media_type(node)
                post_id = node.get('pk', str(post_index))

                # Handle single media posts
                if media_type == 'image':
                    image_data = self._extract_image_data(node, post_index)
                    if image_data:
                        images.append(image_data)

                elif media_type == 'video' and video_settings.get('download_videos', True):
                    video_data = self._extract_video_data(node, post_index, video_settings)
                    if video_data:
                        videos.append(video_data)

                # Handle carousel posts
                elif media_type == 'carousel':
                    carousel_media = node.get('carousel_media', [])
                    for media_index, carousel_item in enumerate(carousel_media, 1):
                        carousel_type = self.detect_media_type(carousel_item)

                        if carousel_type == 'image':
                            image_data = self._extract_image_data(carousel_item, post_index, media_index)
                            if image_data:
                                images.append(image_data)

                        elif carousel_type == 'video' and video_settings.get('download_videos', True):
                            video_data = self._extract_video_data(carousel_item, post_index, video_settings, media_index)
                            if video_data:
                                videos.append(video_data)

                post_index += 1

            except Exception as e:
                print(f"Error processing post {post_index}: {e}")
                post_index += 1
                continue

        # Remove duplicates
        unique_images = self._remove_duplicates(images)
        unique_videos = self._remove_duplicates(videos)

        return {
            'images': unique_images,
            'videos': unique_videos
        }

    def _extract_image_data(self, node: dict, post_index: int, media_index: int = 1) -> dict:
        """Extract image data from node"""
        image_versions = node.get('image_versions2', {}).get('candidates', [])
        if not image_versions:
            return None

        best_image = image_versions[0]
        return {
            'url': best_image.get('url'),
            'post_id': node.get('pk', str(post_index)),
            'type': 'image',
            'width': best_image.get('width'),
            'height': best_image.get('height'),
            'post_index': post_index,
            'media_index': media_index
        }

    def _extract_video_data(self, node: dict, post_index: int, video_settings: dict, media_index: int = 1) -> dict:
        """Extract video data from node"""
        video_versions = node.get('video_versions', [])
        if not video_versions:
            return None

        best_video = self.select_best_video_quality(video_versions, video_settings.get('video_quality', 'highest'))
        if not best_video:
            return None

        # Get thumbnail from image_versions2
        thumbnail_url = None
        image_versions = node.get('image_versions2', {}).get('candidates', [])
        if image_versions:
            thumbnail_url = image_versions[0].get('url')

        return {
            'url': best_video.get('url'),
            'post_id': node.get('pk', str(post_index)),
            'type': 'video',
            'video_type': best_video.get('type'),
            'width': best_video.get('width'),
            'height': best_video.get('height'),
            'has_audio': node.get('has_audio', False),
            'product_type': node.get('product_type', 'feed'),
            'thumbnail_url': thumbnail_url,
            'post_index': post_index,
            'media_index': media_index
        }

    def _remove_duplicates(self, media_list: list) -> list:
        """Remove duplicate media items based on URL"""
        seen_urls = set()
        unique_media = []

        for item in media_list:
            url = item.get('url')
            if url and url not in seen_urls:
                unique_media.append(item)
                seen_urls.add(url)

        return unique_media

    def fetch_user_posts(self, username: str, max_pages: int = 10) -> list:
        """Fetch user posts using GraphQL API"""
        print(f"Fetching posts for: {username}")

        fb_dtsg = self._get_fb_dtsg(username)
        all_posts = []
        after_cursor = None
        page = 1

        while page <= max_pages:
            print(f"Fetching page {page}...")

            variables = {
                "data": {
                    "count": 12,
                    "include_reel_media_seen_timestamp": True,
                    "include_relationship_info": True,
                    "latest_besties_reel_media": True,
                    "latest_reel_media": True
                },
                "first": 12,
                "username": username,
                "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
                "__relay_internal__pv__PolarisShareSheetV3relayprovider": True,
                "after": after_cursor,
                "before": None,
                "last": None
            }

            form_data = {
                'av': '17841400513586183',
                '__d': 'www',
                '__user': '0',
                '__a': '1',
                '__req': 'w',
                '__hs': '20295.HYP:instagram_web_pkg.2.1...0',
                'dpr': '1',
                '__ccg': 'GOOD',
                '__rev': '1025183536',
                '__s': '1efvnh:34ifsd:mcet3d',
                '__hsi': '7531304946230259981',
                '__comet_req': '7',
                'fb_dtsg': fb_dtsg,
                'jazoest': '26315',
                'lsd': 'AqyAlacDTljnYi-rkSLPfx',
                '__spin_r': '1025183536',
                '__spin_b': 'trunk',
                '__spin_t': str(int(time.time())),
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'PolarisProfilePostsTabContentQuery_connection',
                'variables': json.dumps(variables),
                'server_timestamps': 'true',
                'doc_id': self.doc_id
            }

            headers = self.session.headers.copy()
            headers['X-CSRFToken'] = self.csrf_token

            try:
                response = self.session.post(
                    'https://www.instagram.com/graphql/query',
                    data=form_data,
                    headers=headers,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    timeline_data = data.get('data', {}).get('xdt_api__v1__feed__user_timeline_graphql_connection', {})
                    edges = timeline_data.get('edges', [])

                    if edges:
                        print(f"Found {len(edges)} posts on page {page}")
                        all_posts.extend(edges)

                        page_info = timeline_data.get('page_info', {})
                        has_next_page = page_info.get('has_next_page', False)
                        after_cursor = page_info.get('end_cursor')

                        if not has_next_page or not after_cursor:
                            print("No more pages available")
                            break
                    else:
                        print("No posts found on this page")
                        break
                else:
                    print(f"Request failed: {response.status_code}")
                    break

            except Exception as e:
                print(f"Request error: {e}")
                break

            time.sleep(random.uniform(2, 4))
            page += 1

        print(f"Total posts fetched: {len(all_posts)}")
        return all_posts
