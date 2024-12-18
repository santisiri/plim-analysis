import librosa
import numpy as np
import soundfile as sf
import os
import gc

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
        
        # Load audio file in chunks
        print("- Loading audio file")
        duration = librosa.get_duration(path=audio_path)
        
        # Load only first 60 seconds if file is longer
        MAX_DURATION = 60  # seconds
        if duration > MAX_DURATION:
            print(f"- File duration: {duration:.1f}s. Analyzing first {MAX_DURATION}s only")
            y, sr = librosa.load(audio_path, mono=True, duration=MAX_DURATION)
        else:
            y, sr = librosa.load(audio_path, mono=True)
        
        # Extract features
        features = {}
        features['duration'] = float(duration)  # Store full duration
        
        # Tempo
        print("- Calculating tempo")
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # MFCCs
        print("- Extracting MFCCs")
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
        del mfccs  # Free memory
        
        # Spectral Centroid
        print("- Calculating spectral centroid")
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = float(cent.mean())
        del cent  # Free memory
        
        # Zero Crossing Rate
        print("- Calculating zero crossing rate")
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zcr_mean'] = float(zcr.mean())
        del zcr  # Free memory
        
        # Clean up
        del y
        gc.collect()  # Force garbage collection
        
        print(f"""
Analysis results:
- Full Duration: {features['duration']:.2f} seconds
- Analyzed Duration: {min(duration, MAX_DURATION):.2f} seconds
- Tempo: {features['tempo']:.2f} BPM
- Spectral Centroid: {features['spectral_centroid_mean']:.2f} Hz
- Zero Crossing Rate: {features['zcr_mean']:.4f}
        """)
        
        return features
        
    except Exception as e:
        print(f"Error analyzing audio: {str(e)}")
        raise
    finally:
        # Ensure memory is freed
        gc.collect()