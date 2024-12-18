import logging
from pathlib import Path
from data_reader import read_youtube_data
from video_processor import download_audio
from audio_analyzer import analyze_audio
from result_writer import save_results

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,  # Set to INFO to avoid system debug messages
    format='%(message)s',  # Only show the message itself
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Disable logging for third-party libraries
logging.getLogger('yt_dlp').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('librosa').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    try:
        # Create necessary directories
        Path("downloads").mkdir(exist_ok=True)
        Path("results").mkdir(exist_ok=True)
        
        # Read YouTube data
        print("\n=== Reading YouTube Data ===")
        df = read_youtube_data("bebefinn.xlsx")
        total_videos = len(df)
        print(f"\nFound {total_videos} videos to process\n")
        
        # Process each video
        results = []
        successful = 0
        failed = 0
        
        print("=== Processing Videos ===")
        for idx, row in df.iterrows():
            try:
                video_url = row['url']
                views = row['views']
                print(f"\nProcessing video {idx + 1}/{total_videos}")
                print(f"URL: {video_url}")
                print(f"Views: {views:,}")
                
                # Download audio
                audio_path = download_audio(video_url)
                if audio_path:
                    # Analyze audio
                    features = analyze_audio(audio_path)
                    features['url'] = video_url
                    features['views'] = views
                    results.append(features)
                    successful += 1
                    print(f"✓ Successfully processed video {idx + 1}/{total_videos}")
                else:
                    failed += 1
                    print(f"✗ Failed to download video {idx + 1}/{total_videos}")
                
            except Exception as e:
                failed += 1
                print(f"✗ Error processing video: {str(e)}")
                continue
        
        # Save results
        if results:
            print("\n=== Saving Results ===")
            save_results(results)
            success_rate = (successful/total_videos)*100
            print(f"""
Analysis completed!
--------------------
Total videos: {total_videos}
Successfully processed: {successful}
Failed: {failed}
Success rate: {success_rate:.1f}%
            """)
        else:
            print("\nNo results to save!")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n=== Starting YouTube Video Audio Analysis ===")
    main()
    print("\n=== Analysis Process Completed ===\n") 