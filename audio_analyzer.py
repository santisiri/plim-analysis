import librosa
import numpy as np
import soundfile as sf
import os

def analyze_audio(audio_path: str) -> dict:
    """
    Extract audio features using librosa.
    
    Args:
        audio_path (str): Path to audio file (mp4)
        
    Returns:
        dict: Dictionary containing extracted features
    """
    try:
        print("\nAnalyzing audio...")
        
        # Load audio file
        y, sr = librosa.load(audio_path, mono=True)
        duration = len(y) / sr
        
        # Extract features
        features = {}
        
        # Tempo
        print("- Calculating tempo")
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # MFCCs
        print("- Extracting MFCCs")
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
        
        # Spectral Centroid
        print("- Calculating spectral centroid")
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = float(cent.mean())
        
        # Zero Crossing Rate
        print("- Calculating zero crossing rate")
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zcr_mean'] = float(zcr.mean())
        
        # Add duration
        features['duration'] = float(duration)
        
        print(f"""
Analysis results:
- Duration: {features['duration']:.2f} seconds
- Tempo: {features['tempo']:.2f} BPM
- Spectral Centroid: {features['spectral_centroid_mean']:.2f} Hz
- Zero Crossing Rate: {features['zcr_mean']:.4f}
        """)
        
        return features
        
    except Exception as e:
        print(f"Error analyzing audio: {str(e)}")
        raise