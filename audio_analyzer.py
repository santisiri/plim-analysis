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
        logger.info(f"Starting audio analysis for: {audio_path}")
        
        # Load audio file
        logger.debug("Loading audio file...")
        y, sr = librosa.load(audio_path, mono=True)
        duration = len(y) / sr
        logger.debug(f"Audio loaded - Duration: {duration:.2f}s, Sample rate: {sr}Hz")
        
        # Extract features
        features = {}
        
        # Tempo
        logger.debug("Calculating tempo...")
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        logger.debug(f"Detected tempo: {tempo:.2f} BPM with {len(beats)} beats")
        
        # MFCCs
        logger.debug("Extracting MFCCs...")
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
        logger.debug(f"Extracted {len(features['mfcc_mean'])} MFCC coefficients")
        
        # Spectral Centroid
        logger.debug("Calculating spectral centroid...")
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = float(cent.mean())
        logger.debug(f"Average spectral centroid: {features['spectral_centroid_mean']:.2f} Hz")
        
        # Zero Crossing Rate
        logger.debug("Calculating zero crossing rate...")
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zcr_mean'] = float(zcr.mean())
        logger.debug(f"Average zero crossing rate: {features['zcr_mean']:.4f}")
        
        # Add duration
        features['duration'] = float(duration)
        
        logger.info(f"""
Audio analysis completed:
- Duration: {features['duration']:.2f} seconds
- Tempo: {features['tempo']:.2f} BPM
- Spectral Centroid: {features['spectral_centroid_mean']:.2f} Hz
- Zero Crossing Rate: {features['zcr_mean']:.4f}
        """)
        
        return features
        
    except Exception as e:
        logger.error(f"Error analyzing audio file: {audio_path}", exc_info=True)
        raise