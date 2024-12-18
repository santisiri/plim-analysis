import logging
from pathlib import Path
from data_reader import read_youtube_data
from video_processor import download_audio
from audio_analyzer import analyze_audio
from result_writer import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Create necessary directories
        Path("downloads").mkdir(exist_ok=True)
        Path("results").mkdir(exist_ok=True)
        
        # Read YouTube data
        logger.info("Reading YouTube data from Excel file...")
        df = read_youtube_data("bebefinn.xlsx")
        total_videos = len(df)
        logger.info(f"Processing {total_videos} videos in total")
        
        # Process each video
        results = []
        successful = 0
        failed = 0
        
        for idx, row in df.iterrows():
            try:
                video_url = row['url']
                logger.info(f"Processing video {idx + 1}/{total_videos}: {video_url}")
                
                # Download audio
                audio_path = download_audio(video_url)
                if audio_path:
                    # Analyze audio
                    features = analyze_audio(audio_path)
                    features['url'] = video_url
                    features['views'] = row['views']
                    results.append(features)
                    successful += 1
                    logger.info(f"Successfully processed video {idx + 1}/{total_videos}")
                else:
                    failed += 1
                    logger.warning(f"Failed to download video {idx + 1}/{total_videos}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Error processing video {video_url}: {str(e)}")
                continue
        
        # Save results
        if results:
            save_results(results)
            logger.info(f"""
            Analysis completed!
            Total videos: {total_videos}
            Successfully processed: {successful}
            Failed: {failed}
            Success rate: {(successful/total_videos)*100:.1f}%
            """)
        else:
            logger.warning("No results to save!")
            
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 