from visualizer import app
import os
import json
import pandas as pd
from datetime import datetime

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Run server
    app.run_server(
        host='0.0.0.0',  # Required for cloud deployment
        port=port,
        debug=False  # Set to False in production
    ) 

def export_advanced_analysis(analysis_results):
    # Export detailed JSON results
    with open('results/analysis_results.json', 'w') as f:
        json.dump({
            'audio_features': analysis_results['features'],
            'patterns': analysis_results['patterns'],
            'temporal_analysis': analysis_results['temporal'],
            'metadata': {
                'analysis_version': '2.0',
                'timestamp': datetime.now().isoformat()
            }
        }, f, indent=2)
    
    # Export CSV for easier statistical analysis
    df = pd.DataFrame(analysis_results['features'])
    df.to_csv('results/analysis_results.csv', index=False) 