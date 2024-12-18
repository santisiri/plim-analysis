from pathlib import Path
import yt_dlp
import time

def download_audio(url: str, max_retries: int = 3) -> str:
    """
    Download audio from YouTube video using yt-dlp without FFmpeg.
    
    Args:
        url (str): YouTube video URL
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: Path to downloaded audio file
    """
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
            Path("downloads").mkdir(exist_ok=True)
            
            # Download the audio
            print(f"Download attempt {attempt + 1}/{max_retries}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                ext = info['ext']
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 'Unknown')
                
                audio_path = str(Path('downloads') / f"{video_id}.{ext}")
                print(f"""
Downloaded successfully:
- Title: {title}
- Duration: {duration} seconds
- Format: {ext}
                """)
                return audio_path
                
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Download failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # Exponential backoff
                continue
            print(f"All download attempts failed")
            return None

    return None 