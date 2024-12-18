import logging
from pathlib import Path
import yt_dlp
import time

logger = logging.getLogger(__name__)

def download_audio(url: str, max_retries: int = 3) -> str:
    """
    Download audio from YouTube video using yt-dlp without FFmpeg.
    
    Args:
        url (str): YouTube video URL
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: Path to downloaded audio file
    """
    logger.debug(f"Configuring yt-dlp options for URL: {url}")
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]',  # Only download m4a audio
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_audio': True,
        'postprocessors': [],  # No post-processing
        'http_headers': {  # Add headers to avoid some restrictions
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    
    for attempt in range(max_retries):
        try:
            # Create downloads directory if it doesn't exist
            logger.debug("Ensuring downloads directory exists")
            Path("downloads").mkdir(exist_ok=True)
            
            # Download the audio
            logger.info(f"Starting download attempt {attempt + 1}/{max_retries} for {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug("Extracting video information...")
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                ext = info['ext']
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 'Unknown')
                
                audio_path = str(Path('downloads') / f"{video_id}.{ext}")
                logger.info(f"""
Successfully downloaded audio:
- Title: {title}
- Video ID: {video_id}
- Duration: {duration} seconds
- Format: {ext}
- Saved to: {audio_path}
                """)
                return audio_path
                
        except Exception as e:
            logger.error(f"Error during download attempt {attempt + 1}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)  # Exponential backoff
                continue
            logger.error(f"All {max_retries} download attempts failed for {url}")
            return None

    logger.error(f"Failed to download audio after {max_retries} attempts")
    return None 