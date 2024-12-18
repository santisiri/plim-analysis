from pathlib import Path
import yt_dlp
import time
import subprocess
import os
import gc
import shutil

def get_free_space(path: str) -> float:
    """Return free space in GB."""
    stats = shutil.disk_usage(path)
    return stats.free / (1024 * 1024 * 1024)  # Convert to GB

def cleanup_files(file_path: str):
    """Clean up temporary files."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}")

def cleanup_downloads_folder():
    """Clean up all files in downloads folder."""
    try:
        downloads_path = Path("downloads")
        if downloads_path.exists():
            for file in downloads_path.glob("*"):
                cleanup_files(str(file))
        print("Cleaned up downloads folder")
    except Exception as e:
        print(f"Error cleaning up downloads folder: {str(e)}")

def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format using ffmpeg."""
    try:
        output_path = str(Path(input_path).with_suffix('.wav'))
        print("Converting audio to WAV format...")
        
        # Run ffmpeg to convert the file with lower quality to save space
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',  # Use standard WAV codec
            '-ar', '22050',          # Lower sample rate (was 44100)
            '-ac', '1',              # Mono
            '-y',                    # Overwrite output file
            output_path
        ], check=True, capture_output=True)
        
        # Remove the original file
        cleanup_files(input_path)
        print("Conversion completed successfully")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e.stderr.decode()}")
        cleanup_files(input_path)
        return None
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        cleanup_files(input_path)
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
    # Check available disk space (need at least 500MB)
    MIN_SPACE_GB = 0.5
    if get_free_space(".") < MIN_SPACE_GB:
        print(f"Low disk space! Cleaning up downloads folder...")
        cleanup_downloads_folder()
        if get_free_space(".") < MIN_SPACE_GB:
            print(f"Error: Insufficient disk space (need at least {MIN_SPACE_GB}GB free)")
            return None
    
    ydl_opts = {
        'format': 'worstaudio',  # Use lowest quality audio to save space
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_audio': True,
        'postprocessors': [],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    
    audio_path = None
    wav_path = None
    
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
                cleanup_files(audio_path)
                cleanup_files(wav_path)
                time.sleep(wait_time)
                continue
            print(f"All download attempts failed")
            cleanup_files(audio_path)
            cleanup_files(wav_path)
            return None
        finally:
            gc.collect()

    return None 