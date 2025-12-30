# TubeFetch

A powerful and user-friendly YouTube video and playlist downloader built with Streamlit. Download videos as MP4 or extract audio as MP3 with support for subtitles, metadata, and playlist management.

## Features

- **Video & Playlist Downloads**: Download individual YouTube videos or entire playlists
- **Format Options**: 
  - MP4 video format (up to 1080p)
  - MP3 audio format with album art support
- **Subtitle Support**: Automatically download subtitles in SRT format
- **Playlist Management**: 
  - Batch download playlists
  - Optional automatic ZIP compression
  - Album mode for audio with metadata embedding
- **Demo Mode**: Limited functionality for public demos (10 min videos, 5 playlist items) - disable for full access
- **Customizable Output**: Save downloads to any directory
- **FFmpeg Integration**: Automatic video/audio processing

## Requirements

- Python 3.8+
- ffmpeg (system dependency)
- Internet connection

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshgupta2125/TubeFetch.git
   cd TubeFetch
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually install:
   ```bash
   pip install streamlit yt-dlp
   ```

3. **Install ffmpeg** (if not already installed):
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**:
   - Opens automatically at `http://localhost:8501`

3. **Download videos/playlists**:
   - Paste a YouTube video or playlist link
   - Select output folder
   - Choose format (MP3/MP4)
   - Select mode (Single video/Playlist)
   - Configure optional settings
   - Click "Fetch" to start download

## Configuration

Environment variables for advanced customization:

- `TUBEFETCH_DEMO_MODE`: Enable/disable demo mode (default: "1")
- `TUBEFETCH_DEMO_MAX_ITEMS`: Max playlist items in demo mode (default: "5")
- `TUBEFETCH_DEMO_MAX_DURATION`: Max video duration in seconds for demo (default: "600")
- `TUBEFETCH_MAX_HEIGHT`: Maximum video resolution in pixels (default: "1080")

**Example - Disable demo mode and set custom limits**:
```bash
export TUBEFETCH_DEMO_MODE=0
export TUBEFETCH_MAX_HEIGHT=720
streamlit run app.py
```

## Project Structure

```
TubeFetch/
├── app.py                 # Main Streamlit application
├── downloader_funcs.py    # Download logic and utilities
├── packages.txt           # System dependencies
└── README.md              # Documentation
```

## Key Components

### app.py
- Streamlit web interface
- User input handling
- Configuration controls
- Download progress display

### downloader_funcs.py
- YouTube download functionality using `yt-dlp`
- Format conversion and post-processing
- Error handling and validation
- FFmpeg integration

## Notes

- **Legal Usage**: This tool is intended for personal backups of content you have rights to download
- **Respect Creators**: Always respect copyright and creators' rights
- **Demo Mode**: The public demo has limitations to conserve resources
- **Local Use**: Clone the repository for unrestricted functionality

## Troubleshooting

**Issue**: "ffmpeg not found"
- **Solution**: Install ffmpeg using your system's package manager (see Installation section)

**Issue**: Download fails
- **Solution**: 
  - Check internet connection
  - Verify YouTube URL is valid and accessible
  - Ensure output folder has write permissions
  - Check that `yt-dlp` is up to date: `pip install --upgrade yt-dlp`

**Issue**: Subtitle download fails
- **Solution**: Some videos may not have subtitles available; try with subtitle mode set to "auto"

## Contributing

Feel free to fork, modify, and improve this project for your personal use.

## License

This project is provided as-is for educational and personal use.

## Author

Created by [harshgupta2125](https://github.com/harshgupta2125)