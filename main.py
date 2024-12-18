import logging
from pathlib import Path
from data_reader import read_youtube_data
from video_processor import download_audio, cleanup_files, cleanup_downloads_folder, get_free_space
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
        # Clean up any leftover files from previous runs
        print("\n=== Cleaning up old files ===")
        cleanup_downloads_folder()
        
        # Create necessary directories
        Path("downloads").mkdir(exist_ok=True)
        Path("results").mkdir(exist_ok=True)
        
        # Check initial disk space
        free_space = get_free_space(".")
        print(f"\nAvailable disk space: {free_space:.2f}GB")
        
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
                
                # Check disk space before each download
                free_space = get_free_space(".")
                print(f"Available disk space: {free_space:.2f}GB")
                
                # Download audio
                audio_path = download_audio(video_url)
                if audio_path:
                    try:
                        # Analyze audio
                        features = analyze_audio(audio_path)
                        features['url'] = video_url
                        features['views'] = views
                        results.append(features)
                        successful += 1
                        print(f"✓ Successfully processed video {idx + 1}/{total_videos}")
                    finally:
                        # Clean up audio file after analysis
                        cleanup_files(audio_path)
                else:
                    failed += 1
                    print(f"✗ Failed to download video {idx + 1}/{total_videos}")
                
            except Exception as e:
                failed += 1
                print(f"✗ Error processing video: {str(e)}")
                continue
            finally:
                # Clean up any remaining files after each video
                cleanup_downloads_folder()
        
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
    finally:
        # Final cleanup
        print("\n=== Final Cleanup ===")
        cleanup_downloads_folder()

if __name__ == "__main__":
    print("\n=== Starting YouTube Video Audio Analysis ===")
    main()
    print("\n=== Analysis Process Completed ===\n") 