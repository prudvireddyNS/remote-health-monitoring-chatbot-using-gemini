import os

# Get API key from environment variable or set a default value
apiKey = os.getenv('GEMINI_API_KEY', '')

if not apiKey:
    print("Warning: GEMINI_API_KEY environment variable not set. Please set it to use the Gemini API.")