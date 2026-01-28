"""
Callback Service - GUVI Hackathon Compliant
Handles: Sending final results to GUVI's callback endpoint
"""

import httpx
from ..config import settings
from ..models import ExtractedIntelligence
import logging

logger = logging.getLogger(__name__)


class CallbackService:
    """
    Service to report final results to GUVI.
    
    IMPORTANT: This should only be called ONCE per conversation,
    at the end when we have:
    - Confirmed scam detection
    - Sufficient engagement
    - Extracted intelligence
    """
    
    async def send_final_result(
        self, 
        session_id: str, 
        scam_detected: bool, 
        total_messages: int,
        intel: ExtractedIntelligence,
        agent_notes: str
    ) -> bool:
        """
        Send the final result to GUVI's callback endpoint.
        
        Payload format matches GUVI's expected structure exactly.
        """
        
        # GUVI's expected format (Section 12 of requirements doc)
        # totalMessagesExchanged is at ROOT level, NOT nested
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,  # At root level per GUVI spec
            "extractedIntelligence": {
                "bankAccounts": intel.bankAccounts,
                "upiIds": intel.upiIds,
                "phishingLinks": intel.phishingLinks,
                "phoneNumbers": intel.phoneNumbers,
                "suspiciousKeywords": intel.suspiciousKeywords
            },
            "agentNotes": agent_notes
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        callback_url = settings.GUVI_CALLBACK_URL
        
        if not callback_url:
            logger.warning(f"[{session_id}] No callback URL configured, skipping callback")
            return False
        
        logger.info(f"[{session_id}] Sending final callback to {callback_url}")
        logger.debug(f"[{session_id}] Payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    callback_url, 
                    json=payload, 
                    headers=headers,
                    timeout=15.0  # Slightly longer timeout for reliability
                )
                response.raise_for_status()
                
                logger.info(f"[{session_id}] Callback SUCCESS: {response.status_code}")
                return True
                
            except httpx.TimeoutException:
                logger.error(f"[{session_id}] Callback TIMEOUT after 15 seconds")
                return False
            except httpx.HTTPStatusError as e:
                logger.error(f"[{session_id}] Callback HTTP ERROR: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"[{session_id}] Callback FAILED: {type(e).__name__}: {e}")
                return False
