from visualizer import app
import os

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Run server
    app.run_server(
        host='0.0.0.0',  # Required for cloud deployment
        port=port,
        debug=False  # Set to False in production
    ) 