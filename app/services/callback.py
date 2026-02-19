"""
Callback Service - GUVI Hackathon Grand Finale
Handles: Sending final results to GUVI's callback endpoint

Payload format matches the evaluation system's expected structure:
- status: "success"
- scamDetected: boolean
- scamType: string
- extractedIntelligence: {phoneNumbers, bankAccounts, upiIds, phishingLinks, emailAddresses}
- engagementMetrics: {totalMessagesExchanged, engagementDurationSeconds}
- agentNotes: string
"""

import httpx
from ..config import settings
from ..models import ExtractedIntelligence
import logging

logger = logging.getLogger(__name__)


class CallbackService:
    """
    Service to report final results to GUVI.
    
    Called as a background task when engagement threshold is reached.
    The evaluator takes the last callback received, so sending multiple
    times (with increasingly complete data) is safe and beneficial.
    """
    
    async def send_final_result(
        self, 
        session_id: str, 
        scam_detected: bool, 
        scam_type: str,
        total_messages: int,
        duration_seconds: int,
        intel: ExtractedIntelligence,
        agent_notes: str,
        confidence_level: float = 0.95
    ) -> bool:
        """
        Send the final result to GUVI's callback endpoint.
        
        Feb 19 format: includes sessionId, confidenceLevel, new intel types,
        root-level engagement fields.
        """
        
        # Build payload with ALL fields from Feb 19 rubric
        payload = {
            "sessionId": session_id,
            "status": "success",
            "scamDetected": scam_detected,
            "scamType": scam_type,
            "confidenceLevel": round(confidence_level, 2),
            # Root-level engagement (1pt structure)
            "totalMessagesExchanged": total_messages,
            "engagementDurationSeconds": duration_seconds,
            "extractedIntelligence": {
                "phoneNumbers": intel.phoneNumbers,
                "bankAccounts": intel.bankAccounts,
                "upiIds": intel.upiIds,
                "phishingLinks": intel.phishingLinks,
                "emailAddresses": intel.emailAddresses,
                "caseIds": intel.caseIds,
                "policyNumbers": intel.policyNumbers,
                "orderNumbers": intel.orderNumbers
            },
            "engagementMetrics": {
                "totalMessagesExchanged": total_messages,
                "engagementDurationSeconds": duration_seconds
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
        
        logger.info(f"[{session_id}] Sending callback to {callback_url}")
        logger.info(f"[{session_id}] Callback payload: scamDetected={scam_detected}, "
                     f"scamType={scam_type}, messages={total_messages}, "
                     f"duration={duration_seconds}s, "
                     f"phones={intel.phoneNumbers}, banks={intel.bankAccounts}, "
                     f"upis={intel.upiIds}, links={intel.phishingLinks}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    callback_url, 
                    json=payload, 
                    headers=headers,
                    timeout=15.0  # Generous timeout for reliability
                )
                response.raise_for_status()
                
                logger.info(f"[{session_id}] Callback SUCCESS: {response.status_code}")
                return True
                
            except httpx.TimeoutException:
                logger.error(f"[{session_id}] Callback TIMEOUT after 15 seconds")
                return False
            except httpx.HTTPStatusError as e:
                logger.error(f"[{session_id}] Callback HTTP ERROR: {e.response.status_code} - {e.response.text[:200]}")
                return False
            except Exception as e:
                logger.error(f"[{session_id}] Callback FAILED: {type(e).__name__}: {e}")
                return False
