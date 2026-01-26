
import google.generativeai as genai
from ..config import settings
from ..models import ScamAnalysis, Message
from typing import List
import json

class ScamDetectorService:
    """Service to detect scam intent using Gemini AI."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
    async def analyze(self, message: str, history: List[Message]) -> ScamAnalysis:
        """Analyze a message for scam intent."""
        
        # Prepare context from history (last 3 messages is usually enough for context)
        context_str = ""
        if history:
            context_str = "\nPrevious conversation:\n" + "\n".join(
                [f"{msg.sender}: {msg.text}" for msg in history[-3:]]
            )
            
        prompt = f"""
        You are an AI expert in detecting financial scams and fraud.
        Analyze the following incoming message for scam intent.
        
        Incoming Message: "{message}"
        {context_str}
        
        Is this message likely a scam?
        CRITICAL: If the message contains ANY of the following, answer "is_scam": true
        - Threats to block/suspend account
        - Demands to "verify immediately" or "complete KYC"
        - Requests for UPI PIN, passwords, or OTPs
        - Unsolicited lottery or job offers
        - Suspicious links asking for login
        
        Respond in strict JSON format:
        {{
            "is_scam": boolean,
            "confidence": float (0.0 to 1.0),
            "reasoning": "short explanation",
            "detected_patterns": ["list", "of", "scam", "keywords"]
        }}
        """
        
        import asyncio
        
        # Retry logic for robust API calls
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Safety settings to allow scam analysis
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config={"response_mime_type": "application/json"},
                    safety_settings=safety_settings
                )
                
                # Check if we have a valid part
                if not response.parts:
                    print(f"Gemini Empty Response (Attempt {attempt+1}/{max_retries}). Finish Reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")
                    # Fallback to text parsing if parts are weird but text exists in candidates
                    if response.candidates and response.candidates[0].content.parts:
                         text_response = response.candidates[0].content.parts[0].text
                    else:
                         if attempt == max_retries - 1:
                             raise ValueError("Empty response from Gemini after retries")
                         await asyncio.sleep(1 * (attempt + 1)) # Backoff
                         continue
                else:
                    text_response = response.text

                # Cleanup JSON string if model adds markdown blocks
                text_response = text_response.replace("```json", "").replace("```", "").strip()
                result = json.loads(text_response)
                
                return ScamAnalysis(
                    is_scam=result.get("is_scam", False),
                    confidence=result.get("confidence", 0.0),
                    detected_patterns=result.get("detected_patterns", []),
                    reasoning=result.get("reasoning", "")
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Scam detection error: {e}")
                    return ScamAnalysis(is_scam=False, confidence=0.0, reasoning=f"Error: {str(e)}")
                await asyncio.sleep(1 * (attempt + 1))

    async def analyze_dummy(self, is_scam: bool = True) -> ScamAnalysis:
        """Fast return for established conversations."""
        return ScamAnalysis(
            is_scam=is_scam,
            confidence=1.0,
            detected_patterns=["established_context"],
            reasoning="Conversation depth implies established context."
        )
