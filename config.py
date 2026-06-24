# config.py - All your settings
import os
from dotenv import load_dotenv

# Load your secret keys from .env file
load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model settings (all FREE on Groq)
    MODEL_NAME = "llama-3.3-70b-versatile"  # Best free model
    
    # Temperature (0 = strict, 1 = creative)
    TEMPERATURE = 0.7
    
    # Max tokens (response length)
    MAX_TOKENS = 500
    
    # Language settings
    SUPPORTED_LANGUAGES = [
        "en", "hi", "es", "fr", "de", "zh", "ar", 
        "pt", "ru", "ja", "ko", "it", "nl", "pl"
    ]
    
    # Cache settings
    CACHE_SIZE = 100  # Remember last 100 questions