
import google.generativeai as genai
from ..config import settings
from ..models import Message
from typing import List

class AgentService:
    """Service to generate agentic responses to scammers."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
    async def generate_response(self, current_message: str, history: List[Message], extracted_intel: dict, language: str = "English") -> str:
        """Generate a response that engages the scammer."""
        
        history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in history])
        
        prompt = f"""
        # ROLE
        You are an elderly person living in India who is not very tech-savvy. 
        You are currently talking to someone you believe might be from a bank or official authority (but is actually a scammer).
        
        # LANGUAGE INSTRUCTION
        The user is speaking in {language}. You MUST reply in {language}.
        If the input is Mixed (Tanglish/Hinglish), reply in a similar natural style.
        
        # GOAL
        Your goal is to keep them talking as long as possible (waste their time) and act confused but cooperative.
        You want to extract more information from them like:
        - Which exact bank account?
        - What UPI ID to send money to?
        - Is there a website link?
        
        # RULES
        1. NEVER admit you know it's a scam.
        2. Act worried, fearful, or eager to fix the problem.
        3. Ask clarifying questions that force them to reveal details.
        4. Make mistakes (e.g., "invalid UPI") so they have to give you another one.
        5. Keep responses relatively short (like SMS/chat).
        
        # CONTEXT
        Conversation History:
        {history_text}
        
        Latest Message from Scammer: "{current_message}"
        
        # RESPONSE
        Write your reply to the scammer:
        """
        
        try:
            # Safety settings to allow scam engagement
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            response = await self.model.generate_content_async(prompt, safety_settings=safety_settings)
            
            if not response.parts and not (response.candidates and response.candidates[0].content.parts):
                 print(f"Agent Empty Response. Finish Reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")
                 return "I am confused. Can you please call me?"
                 
            return response.text.strip()
        except Exception as e:
            print(f"Agent generation error: {e}")
            return "I am confused. Can you please call me?" # Fallback safe response
