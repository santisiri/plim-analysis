from pathlib import Path
import yt_dlp
import time
import subprocess
import os
import gc
import shutil
import librosa
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose

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

def analyze_audio_features(audio_data):
    # Extract advanced audio features
    features = {
        'spectral_centroid': librosa.feature.spectral_centroid(y=audio_data),
        'spectral_rolloff': librosa.feature.spectral_rolloff(y=audio_data),
        'zero_crossing_rate': librosa.feature.zero_crossing_rate(y=audio_data),
        'chroma_features': librosa.feature.chroma_stft(y=audio_data),
        'tempo': librosa.beat.tempo(y=audio_data)[0],
        'harmonic_percussive': librosa.effects.hpss(y=audio_data)
    }
    
    # Calculate statistical measures
    feature_stats = {
        'energy_mean': np.mean(librosa.feature.rms(y=audio_data)),
        'energy_var': np.var(librosa.feature.rms(y=audio_data)),
        'tempo_stability': calculate_tempo_stability(audio_data),
        'rhythm_strength': analyze_rhythm_strength(audio_data)
    }
    
    return {**features, **feature_stats}

def calculate_tempo_stability(audio_data):
    # Analyze tempo variations over time windows
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=audio_data, hop_length=hop_length)
    tempo_frames = librosa.util.frame(onset_env, frame_length=128, hop_length=32)
    tempos = np.array([librosa.beat.tempo(onset_envelope=frame) for frame in tempo_frames])
    return np.std(tempos)  # Lower value indicates more stable tempo

def identify_song_patterns(songs_data):
    # Prepare feature matrix
    features_matrix = []
    for song in songs_data:
        features = [
            song['tempo'],
            song['energy_mean'],
            song['spectral_centroid'].mean(),
            song['zero_crossing_rate'].mean()
        ]
        features_matrix.append(features)
    
    # Normalize features
    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(features_matrix)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=5)
    clusters = kmeans.fit_predict(normalized_features)
    
    return clusters, kmeans.cluster_centers_

def analyze_temporal_patterns(audio_data):
    # Convert audio data to time series
    rms_energy = librosa.feature.rms(y=audio_data)[0]
    
    # Perform seasonal decomposition
    decomposition = seasonal_decompose(rms_energy, period=len(rms_energy)//8)
    
    return {
        'trend': decomposition.trend,
        'seasonal': decomposition.seasonal,
        'residual': decomposition.resid
    }

def analyze_rhythm_strength(audio_data):
    """Analyze rhythm characteristics and strength"""
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=audio_data, hop_length=hop_length)
    pulse = librosa.beat.plp(onset_envelope=onset_env, sr=22050)
    
    return {
        'pulse_strength': np.mean(pulse),
        'rhythm_regularity': np.std(pulse),
        'beat_positions': librosa.beat.beat_track(onset_envelope=onset_env)[1]
    }

def analyze_melodic_content(audio_data, sr=22050):
    """Analyze melodic characteristics"""
    # Extract pitch content
    pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
    
    # Calculate pitch statistics
    pitch_mean = np.mean(pitches[magnitudes > np.median(magnitudes)])
    pitch_std = np.std(pitches[magnitudes > np.median(magnitudes)])
    
    # Extract melody contour
    melody = librosa.feature.melodia(
        y=audio_data,
        sr=sr,
        hop_length=128
    )
    
    return {
        'pitch_mean': pitch_mean,
        'pitch_variability': pitch_std,
        'melody_contour': melody,
        'pitch_range': np.ptp(pitches[magnitudes > 0])
    }

def analyze_structural_segments(audio_data, sr=22050):
    """Analyze song structure and segments"""
    # Compute spectrogram
    mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
    
    # Detect structural boundaries
    bound_frames = librosa.segment.detect_onsets(
        librosa.power_to_db(mfcc),
        backtrack=True
    )
    
    # Convert frames to time
    boundaries = librosa.frames_to_time(bound_frames)
    
    # Analyze segment characteristics
    segments = []
    for i in range(len(boundaries)-1):
        start = int(boundaries[i] * sr)
        end = int(boundaries[i+1] * sr)
        segment_data = audio_data[start:end]
        
        segments.append({
            'start_time': boundaries[i],
            'end_time': boundaries[i+1],
            'duration': boundaries[i+1] - boundaries[i],
            'energy': np.mean(librosa.feature.rms(y=segment_data)),
            'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=segment_data))
        })
    
    return {
        'segment_boundaries': boundaries,
        'segment_details': segments,
        'num_segments': len(segments)
    }