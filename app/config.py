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
    GROQ_MODEL: str = "moonshotai/kimi-k2-instruct-0905"  # 60 RPM, 300K TPD (best limits on Groq free tier)
    
    # Cerebras Settings (Round-robin LLM partner)
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_MODEL: str = "llama3.1-8b"  # 30 RPM, 14.4K RPD (zai-glm-4.7 only 10 RPM — unusable)
    CEREBRAS_BASE_URL: str = "https://api.cerebras.ai/v1"
    
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


