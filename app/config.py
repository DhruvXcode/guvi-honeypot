import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    HONEYPOT_API_KEY: str = os.getenv("HONEYPOT_API_KEY", "")
    
    # GUVI Callback
    GUVI_CALLBACK_URL: str = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")
    
    # Gemini Model
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    def validate(self) -> bool:
        """Validate that all required settings are present."""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        if not self.HONEYPOT_API_KEY:
            raise ValueError("HONEYPOT_API_KEY is required")
        return True

settings = Settings()
