import os
import sys
import streamlit.web.cli as stcli
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

def main():
    # Get the directory of this script
    current_dir = Path(__file__).parent.absolute()
    
    # Set the path to the Streamlit app
    streamlit_app_path = current_dir / "app" / "streamlit_app.py"
    
    # Check if the file exists
    if not streamlit_app_path.exists():
        print(f"Error: Could not find Streamlit app at {streamlit_app_path}")
        return 1
    
    # Set environment variable for API key if not already set
    if not os.environ.get('GEMINI_API_KEY'):
        # Prompt user for API key
        api_key = input("Please enter your Gemini API key (or press Enter to skip): ")
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", str(streamlit_app_path), "--browser.serverAddress=localhost", "--server.port=8501"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()