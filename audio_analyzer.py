import librosa
import numpy as np
import logging
import soundfile as sf
import os

logger = logging.getLogger(__name__)

def analyze_audio(audio_path: str) -> dict:
    """
    Extract audio features using librosa.
    
    Args:
        audio_path (str): Path to audio file (mp4)
        
    Returns:
        dict: Dictionary containing extracted features
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, mono=True)
        
        # Extract features
        features = {}
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
        
        # Spectral Centroid
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = float(cent.mean())
        
        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zcr_mean'] = float(zcr.mean())
        
        # Add duration
        features['duration'] = float(len(y) / sr)
        
        return features
        
    except Exception as e:
        logger.error(f"Error analyzing audio file {audio_path}: {str(e)}")
        raise 