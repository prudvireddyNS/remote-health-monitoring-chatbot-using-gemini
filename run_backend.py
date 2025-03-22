import os
import sys
import uvicorn

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Run the FastAPI application
if __name__ == "__main__":
    print("Starting the Health Monitoring API server...")
    print("API will be available at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)