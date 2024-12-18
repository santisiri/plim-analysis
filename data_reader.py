import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_youtube_data(excel_path: str) -> pd.DataFrame:
    """
    Read YouTube data from Excel file.
    
    Args:
        excel_path (str): Path to Excel file
        
    Returns:
        pd.DataFrame: DataFrame containing all videos
    """
    try:
        logger.info(f"Reading Excel file: {excel_path}")
        
        # Read Excel file
        logger.debug("Loading Excel file into DataFrame...")
        df = pd.read_excel(excel_path)
        logger.debug(f"Successfully loaded {len(df)} rows from Excel file")
        
        # Convert column names to lowercase for case-insensitive comparison
        logger.debug("Converting column names to lowercase...")
        original_columns = list(df.columns)
        df.columns = df.columns.str.lower()
        logger.debug(f"Original columns: {original_columns}")
        logger.debug(f"Converted columns: {list(df.columns)}")
        
        # Verify required columns exist
        required_columns = ['url', 'views']
        logger.debug(f"Checking for required columns: {required_columns}")
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug("All required columns found")
        
        # Sort by views for better visualization but keep all videos
        logger.debug("Sorting videos by view count...")
        df_sorted = df.sort_values('views', ascending=False)
        
        # Log some statistics about the data
        total_views = df_sorted['views'].sum()
        avg_views = df_sorted['views'].mean()
        logger.info(f"""
Data loading completed:
- Total videos: {len(df_sorted)}
- Total views across all videos: {total_views:,.0f}
- Average views per video: {avg_views:,.0f}
- Most viewed video: {df_sorted['views'].max():,.0f} views
- Least viewed video: {df_sorted['views'].min():,.0f} views
        """)
        
        return df_sorted
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {excel_path}", exc_info=True)
        raise