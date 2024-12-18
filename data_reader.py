import pandas as pd

def read_youtube_data(excel_path: str) -> pd.DataFrame:
    """
    Read YouTube data from Excel file.
    
    Args:
        excel_path (str): Path to Excel file
        
    Returns:
        pd.DataFrame: DataFrame containing all videos
    """
    try:
        print(f"Reading file: {excel_path}")
        
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"Found {len(df)} videos")
        
        # Convert column names to lowercase for case-insensitive comparison
        original_columns = list(df.columns)
        df.columns = df.columns.str.lower()
        
        # Verify required columns exist
        required_columns = ['url', 'views']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            print(error_msg)
            raise ValueError(error_msg)
        
        # Sort by views for better visualization but keep all videos
        df_sorted = df.sort_values('views', ascending=False)
        
        # Print statistics
        total_views = df_sorted['views'].sum()
        avg_views = df_sorted['views'].mean()
        print(f"""
Data summary:
- Total videos: {len(df_sorted)}
- Total views: {total_views:,.0f}
- Average views: {avg_views:,.0f}
- Most viewed: {df_sorted['views'].max():,.0f}
- Least viewed: {df_sorted['views'].min():,.0f}
        """)
        
        return df_sorted
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        raise