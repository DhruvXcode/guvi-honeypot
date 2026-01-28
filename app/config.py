import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration."""
    
    # API Keys
    HONEYPOT_API_KEY: str = os.getenv("HONEYPOT_API_KEY", "")
    
    # GUVI Callback (Mandatory)
    GUVI_CALLBACK_URL: str = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

    # Groq Settings (Primary LLM)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    def validate(self) -> bool:
        """Validate that all required settings are present."""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        if not self.HONEYPOT_API_KEY:
            raise ValueError("HONEYPOT_API_KEY is required")
        return True

settings = Settings()

