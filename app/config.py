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
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"  # 30K TPM! (kimi-k2 only 10K TPM = exhausts after 2 turns)
    
    # Cerebras Settings (Round-robin LLM partner)
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_MODEL: str = "qwen-3-235b-a22b-instruct-2507"  # 30 RPM, 60K TPM — same limits as llama3.1-8b but 235B params + native Hinglish
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


