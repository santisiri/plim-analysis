from pathlib import Path
import yt_dlp
import time
import subprocess
import os

def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format using ffmpeg."""
    try:
        output_path = str(Path(input_path).with_suffix('.wav'))
        print("Converting audio to WAV format...")
        
        # Run ffmpeg to convert the file
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',  # Use standard WAV codec
            '-ar', '44100',  # Standard sample rate
            '-ac', '1',  # Convert to mono
            '-y',  # Overwrite output file if it exists
            output_path
        ], check=True, capture_output=True)
        
        # Remove the original file
        os.remove(input_path)
        print("Conversion completed successfully")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        return None

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
                
                # Convert to WAV format
                wav_path = convert_to_wav(audio_path)
                if wav_path:
                    return wav_path
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Download failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # Exponential backoff
                continue
            print(f"All download attempts failed")
            return None

    return None 