
import httpx
from ..config import settings
from ..models import ExtractedIntelligence
import logging

class CallbackService:
    """Service to report final results to GUVI."""
    
    async def send_final_result(self, 
                                session_id: str, 
                                scam_detected: bool, 
                                total_messages: int, 
                                intel: ExtractedIntelligence,
                                agent_notes: str):
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intel.model_dump(),
            "agentNotes": agent_notes
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logging.info(f"Sending callback for session {session_id} to {settings.GUVI_CALLBACK_URL}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.GUVI_CALLBACK_URL, 
                    json=payload, 
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                logging.info(f"Callback success: {response.status_code}")
                return True
            except Exception as e:
                logging.error(f"Callback failed: {e}")
                return False
