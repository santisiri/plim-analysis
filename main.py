import logging
from pathlib import Path
from data_reader import read_youtube_data
from video_processor import download_audio
from audio_analyzer import analyze_audio
from result_writer import save_results

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG level for maximum verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Create necessary directories
        logger.debug("Creating necessary directories...")
        Path("downloads").mkdir(exist_ok=True)
        logger.debug("Created downloads directory")
        Path("results").mkdir(exist_ok=True)
        logger.debug("Created results directory")
        
        # Read YouTube data
        logger.info("Reading YouTube data from Excel file...")
        df = read_youtube_data("bebefinn.xlsx")
        total_videos = len(df)
        logger.info(f"Found {total_videos} videos to process")
        
        # Process each video
        results = []
        successful = 0
        failed = 0
        
        for idx, row in df.iterrows():
            try:
                video_url = row['url']
                views = row['views']
                logger.info(f"Processing video {idx + 1}/{total_videos}")
                logger.debug(f"Video details - URL: {video_url}, Views: {views:,}")
                
                # Download audio
                logger.debug(f"Attempting to download audio for video {idx + 1}")
                audio_path = download_audio(video_url)
                if audio_path:
                    logger.debug(f"Successfully downloaded audio to: {audio_path}")
                    
                    # Analyze audio
                    logger.debug(f"Starting audio analysis for video {idx + 1}")
                    features = analyze_audio(audio_path)
                    features['url'] = video_url
                    features['views'] = views
                    results.append(features)
                    successful += 1
                    logger.info(f"Successfully processed video {idx + 1}/{total_videos}")
                    logger.debug(f"Extracted features: {features}")
                else:
                    failed += 1
                    logger.warning(f"Failed to download video {idx + 1}/{total_videos}: {video_url}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Error processing video {video_url}", exc_info=True)
                continue
        
        # Save results
        if results:
            logger.info("Saving analysis results...")
            save_results(results)
            success_rate = (successful/total_videos)*100
            logger.info(f"""
Analysis completed!
--------------------
Total videos: {total_videos}
Successfully processed: {successful}
Failed: {failed}
Success rate: {success_rate:.1f}%
            """)
        else:
            logger.warning("No results to save!")
            
    except Exception as e:
        logger.error("An error occurred during execution", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting YouTube video audio analysis")
    main()
    logger.info("Analysis process completed") 