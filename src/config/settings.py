import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and constants."""
    APP_NAME = "JoeG Streamlit Wrapped"
    VERSION = "1.0.0"
    
    # Add any environment-specific configurations
    API_KEY = os.getenv("API_KEY", "")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"