# Instagram Mixed Media Downloader

A clean, organized tool for downloading both images and videos from Instagram profiles with smart file organization and progress tracking.

## 🎯 Features

- **Mixed Media Support**: Downloads both images and videos
- **Smart File Naming**: `post_001_img.jpg`, `post_002_video.mp4`
- **Carousel Support**: Handles multi-media posts
- **Video Quality Selection**: Choose highest/medium/lowest quality
- **Progress Tracking**: Visual progress bars for large downloads
- **Robust Error Handling**: Retry logic and graceful failures
- **Clean Architecture**: Well-organized, maintainable code

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Nouking/instagram-downloader.git
cd instagram-downloader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Cookies
```bash
# Copy the example configuration
cp cookies.conf.example cookies.conf

# Edit cookies.conf with your Instagram credentials
# Get cookies from browser: F12 → Application → Cookies → instagram.com
```

### 4. Setup Configuration
Edit `cookies.conf` with your Instagram credentials:
```conf
username = your_target_username
sessionid = your_session_id_from_browser
csrftoken = your_csrf_token_from_browser
ds_user_id = your_user_id_from_browser

# Video settings
download_videos = true
video_quality = highest
max_video_size_mb = 50
```

### 5. Run the Downloader
```bash
python src/main.py
```

## 📁 Project Structure

```
instagram-downloader/
├── src/                          # Main source code
│   ├── main.py                  # Application entry point
│   ├── core/config.py           # Configuration management
│   ├── extractors/graphql_extractor.py # Instagram API handler
│   ├── downloaders/media_downloader.py # Universal downloader
│   └── utils/file_manager.py    # File operations
├── downloads/                   # Downloaded content (gitignored)
├── cookies.conf.example         # Configuration template
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

## ⚙️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `download_videos` | `true` | Enable/disable video downloads |
| `download_images` | `true` | Enable/disable image downloads |
| `video_quality` | `highest` | Video quality: `highest`, `medium`, `lowest` |
| `max_video_size_mb` | `50` | Skip videos larger than this size |

## 📊 File Organization

Downloads are organized with clear, descriptive names:
```
downloads/username/
├── post_001_img.jpg           # Single image
├── post_002_video.mp4         # Single video
├── post_003_img_01.jpg        # Carousel image 1
├── post_003_img_02.jpg        # Carousel image 2
├── post_004_video_01.mp4      # Carousel video 1
└── post_005_video.mp4         # Another video
```

## 🔒 Privacy & Security

- **No Sensitive Data in Repo**: Your cookies and downloaded content are gitignored
- **Example Configuration**: `cookies.conf.example` provides a safe template
- **Local Downloads**: All content stays on your machine
- **Clean Separation**: Personal data never commits to version control

## 🛠️ How to Get Instagram Cookies

1. **Open Instagram in your browser and login**
2. **Press F12 to open Developer Tools**
3. **Go to Application/Storage → Cookies → https://www.instagram.com**
4. **Copy these values to cookies.conf:**
   - `sessionid`
   - `csrftoken` 
   - `ds_user_id`

## 🎯 Usage Examples

### Download Everything (Images + Videos)
```bash
python src/main.py
```

### Images Only
```conf
# In cookies.conf
download_videos = false
```

### High Quality Videos Only
```conf
# In cookies.conf
download_images = false
video_quality = highest
```

## 🏗️ Architecture Benefits

- **Modular Design**: Clean separation of concerns
- **Type Safety**: Full type hints and documentation
- **Error Handling**: Robust retry logic and graceful failures
- **Progress Tracking**: Visual feedback for long downloads
- **Extensible**: Easy to add new features or media types

## 📝 Requirements

- Python 3.7+
- `requests` library for HTTP operations
- `tqdm` library for progress bars
- Valid Instagram account and cookies

## ⚠️ Important Notes

1. **Respect Instagram's Terms**: Only download content you have permission to access
2. **Rate Limiting**: Built-in delays to avoid overwhelming Instagram's servers
3. **Personal Use**: This tool is for personal backup purposes
4. **Cookie Security**: Never share your cookies.conf file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and personal use only. Please respect Instagram's Terms of Service.
