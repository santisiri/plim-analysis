import pandas as pd
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def save_results(results: list) -> None:
    """
    Save analysis results to CSV and JSON files.
    
    Args:
        results (list): List of dictionaries containing analysis results
    """
    try:
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save to CSV
        csv_path = Path('results') / 'analysis_results.csv'
        df.to_csv(csv_path, index=False)
        
        # Save to JSON (for better preservation of nested structures)
        json_path = Path('results') / 'analysis_results.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=4)
            
        logger.info(f"Results saved to {csv_path} and {json_path}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise 