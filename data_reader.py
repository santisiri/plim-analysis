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
        df = pd.read_excel(excel_path)
        
        # Convert column names to lowercase for case-insensitive comparison
        df.columns = df.columns.str.lower()
        
        # Verify required columns exist
        required_columns = ['url', 'views']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Excel file must contain columns 'Url' and 'Views' (case insensitive)")
        
        # Sort by views for better visualization but keep all videos
        df_sorted = df.sort_values('views', ascending=False)
        
        logger.info(f"Found {len(df_sorted)} videos in the Excel file")
        return df_sorted
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        raise