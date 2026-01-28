"""
Honeypot Route - GUVI Hackathon Compliant
Main API endpoint for scam detection and agent engagement
Handles: Cumulative intel, proper callback timing, channel-aware behavior
"""

from fastapi import APIRouter, Header, HTTPException, Depends, BackgroundTasks
from ..models import HoneypotRequest, HoneypotResponse, ExtractedIntelligence, Message
from ..services.scam_detector import ScamDetectorService
from ..services.agent import AgentService
from ..services.intelligence import IntelligenceService
from ..services.callback import CallbackService
from ..config import settings
import logging
from typing import List

router = APIRouter()

# Initialize services
scam_detector = ScamDetectorService()
agent_service = AgentService()
intelligence_service = IntelligenceService()
callback_service = CallbackService()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: str = Header(...)):
    """Validate the API key."""
    if x_api_key != settings.HONEYPOT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


def extract_cumulative_intel(
    current_message: str, 
    history: List[Message],
    intel_service: IntelligenceService
) -> ExtractedIntelligence:
    """
    Extract intelligence from ALL messages in the conversation.
    This ensures we never miss any intel mentioned in previous messages.
    """
    cumulative_intel = ExtractedIntelligence()
    
    # Extract from all history messages
    for msg in history:
        msg_intel = intel_service.extract(msg.text)
        cumulative_intel = intel_service.merge_intelligence(cumulative_intel, msg_intel)
    
    # Extract from current message
    current_intel = intel_service.extract(current_message)
    cumulative_intel = intel_service.merge_intelligence(cumulative_intel, current_intel)
    
    return cumulative_intel


def should_send_callback(
    is_scam: bool,
    total_messages: int,
    has_significant_intel: bool,
    current_message: str
) -> bool:
    """
    Determine if we should send the final callback to GUVI.
    
    GUVI expects the callback at the END of conversation, not on every message.
    We use heuristics to detect conversation end:
    1. After 10+ messages (sufficient engagement)
    2. If scammer shows signs of leaving (bye, leave me, stop, etc.)
    3. If we have significant intel AND 5+ messages
    """
    if not is_scam:
        return False
    
    # Heuristic 1: Conversation has reached sufficient length
    if total_messages >= 10:
        return True
    
    # Heuristic 2: End-of-conversation signals
    end_signals = [
        "bye", "goodbye", "leave me", "stop", "don't message",
        "wrong number", "i will report", "blocking you",
        "this is waste", "you are fake"
    ]
    msg_lower = current_message.lower()
    for signal in end_signals:
        if signal in msg_lower:
            return True
    
    # Heuristic 3: Have significant intel and reasonable engagement
    if has_significant_intel and total_messages >= 5:
        return True
    
    return False


@router.post("/honeypot", response_model=HoneypotResponse)
async def honeypot_handler(
    request: HoneypotRequest, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Main Honey-Pot Endpoint.
    
    Flow:
    1. Detect scam intent (with smart false-positive handling)
    2. Extract cumulative intelligence from full conversation
    3. Generate appropriate response (victim persona OR normal human)
    4. Send callback to GUVI only at conversation end
    """
    
    current_msg = request.message.text
    session_id = request.sessionId
    history = request.conversationHistory or []
    
    # Get channel and language from metadata
    channel = "WhatsApp"  # Default
    language = "English"  # Default
    
    if request.metadata:
        channel = request.metadata.channel or "WhatsApp"
        language = request.metadata.language or "English"
    
    logger.info(f"[{session_id}] Received message on {channel}: {current_msg[:50]}...")
    
    # ============== STEP 1: SCAM DETECTION ==============
    scam_analysis = await scam_detector.analyze(current_msg, history)
    
    logger.info(f"[{session_id}] Scam analysis: is_scam={scam_analysis.is_scam}, confidence={scam_analysis.confidence:.2f}")
    
    # ============== STEP 2: CUMULATIVE INTEL EXTRACTION ==============
    # Always extract from full history + current message
    cumulative_intel = extract_cumulative_intel(current_msg, history, intelligence_service)
    
    has_significant_intel = any([
        cumulative_intel.bankAccounts,
        cumulative_intel.upiIds,
        cumulative_intel.phishingLinks,
        cumulative_intel.phoneNumbers
    ])
    
    logger.info(f"[{session_id}] Intel extracted: {cumulative_intel.model_dump()}")
    
    # ============== STEP 3: BUILD RESPONSE ==============
    response = HoneypotResponse()
    response.scamDetected = scam_analysis.is_scam
    response.extractedIntelligence = cumulative_intel
    
    # Calculate metrics
    total_messages = len(history) + 2  # History + current scammer msg + our reply
    response.engagementMetrics.totalMessagesExchanged = total_messages
    
    # Calculate duration
    try:
        from dateutil import parser
        end_time = parser.parse(request.message.timestamp)
        start_time = end_time
        if history:
            start_time = parser.parse(history[0].timestamp)
        
        duration = int((end_time - start_time).total_seconds())
        response.engagementMetrics.engagementDurationSeconds = duration
    except Exception as e:
        logger.warning(f"Duration calc error: {e}")
        response.engagementMetrics.engagementDurationSeconds = 0
    
    # ============== STEP 4: GENERATE AGENT RESPONSE ==============
    agent_reply = await agent_service.generate_response(
        current_message=current_msg,
        history=history,
        extracted_intel=cumulative_intel.model_dump(),
        language=language,
        is_scam=scam_analysis.is_scam,
        channel=channel,
        timestamp=request.message.timestamp  # For temporal awareness
    )
    
    response.agentResponse = agent_reply
    
    # Set agent notes based on analysis
    if scam_analysis.is_scam:
        response.agentNotes = f"SCAM DETECTED ({scam_analysis.confidence:.0%} confidence). {scam_analysis.reasoning}"
    else:
        response.agentNotes = f"Non-scam message. {scam_analysis.reasoning}"
    
    logger.info(f"[{session_id}] Agent response: {agent_reply[:50]}...")
    
    # ============== STEP 5: CALLBACK (ONLY AT END) ==============
    should_callback = should_send_callback(
        is_scam=scam_analysis.is_scam,
        total_messages=total_messages,
        has_significant_intel=has_significant_intel,
        current_message=current_msg
    )
    
    if should_callback:
        logger.info(f"[{session_id}] Triggering final callback to GUVI")
        background_tasks.add_task(
            callback_service.send_final_result,
            session_id=session_id,
            scam_detected=True,
            total_messages=total_messages,
            intel=cumulative_intel,
            agent_notes=response.agentNotes
        )
    
    return response


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "honeypot"}
