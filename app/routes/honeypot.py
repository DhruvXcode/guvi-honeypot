
from fastapi import APIRouter, Header, HTTPException, Depends, BackgroundTasks
from ..models import HoneypotRequest, HoneypotResponse, ExtractedIntelligence
from ..services.scam_detector import ScamDetectorService
from ..services.agent import AgentService
from ..services.intelligence import IntelligenceService
from ..services.callback import CallbackService
from ..config import settings
import logging

router = APIRouter()

# Initialize services
scam_detector = ScamDetectorService()
agent_service = AgentService()
intelligence_service = IntelligenceService()
callback_service = CallbackService()

async def verify_api_key(x_api_key: str = Header(...)):
    """Validate the API key."""
    if x_api_key != settings.HONEYPOT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@router.post("/honeypot", response_model=HoneypotResponse)
async def honeypot_handler(
    request: HoneypotRequest, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Main Honey-Pot Endpoint.
    1. Check for scam intent
    2. If scam, engage with AI Agent
    3. Extract intelligence
    """
    
    current_msg = request.message.text
    session_id = request.sessionId
    
    # 1. Detect Scam Intent
    # OPTIMIZATION: If conversation is deep (> 4 messages), assume established scam context
    # to save latency and API costs.
    if len(request.conversationHistory) > 4:
        scam_analysis = await scam_detector.analyze_dummy(is_scam=True)
    else:
        # We analyze if it's a scam based on current message + history
        scam_analysis = await scam_detector.analyze(
            current_msg, 
            request.conversationHistory
        )
    
    response = HoneypotResponse()
    response.scamDetected = scam_analysis.is_scam
    response.extractedIntelligence = ExtractedIntelligence()
    
    # 2. Extract Intelligence (Always do this, even if not confirmed scam yet)
    # Extract from current message
    new_intel = intelligence_service.extract(current_msg)
    
    # 3. Handle Engagement
    if scam_analysis.is_scam:
        # Generate Agent Response
        # Pass language from metadata
        language = request.metadata.language if request.metadata and request.metadata.language else "English"
        
        agent_reply = await agent_service.generate_response(
            current_msg,
            request.conversationHistory,
            new_intel.model_dump(),
            language=language
        )
        response.agentResponse = agent_reply
        response.agentNotes = f"Scam detected. {scam_analysis.reasoning}"
        
        # Merge intelligence
        response.extractedIntelligence = intelligence_service.merge_intelligence(
            response.extractedIntelligence, 
            new_intel
        )
        
        # Calculate metrics (History + 2 for current exchange)
        total_messages = len(request.conversationHistory) + 2 
        response.engagementMetrics.totalMessagesExchanged = total_messages
        
        # Calculate Duration
        try:
            from dateutil import parser
            end_time = parser.parse(request.message.timestamp)
            start_time = end_time
            if request.conversationHistory:
                start_time = parser.parse(request.conversationHistory[0].timestamp)
            
            duration = int((end_time - start_time).total_seconds())
            response.engagementMetrics.engagementDurationSeconds = duration
        except Exception as e:
            logging.error(f"Duration calc error: {e}")
            response.engagementMetrics.engagementDurationSeconds = 0
        
        # 4. Background: Send Callback to GUVI
        # LOGIC CHANGE: Only send callback if we have new intelligence OR periodic (every 5 msgs)
        # to avoid spamming the endpoint.
        
        has_fresh_intel = any([
             new_intel.bankAccounts, 
             new_intel.upiIds, 
             new_intel.phishingLinks,
             new_intel.phoneNumbers
        ])
        
        is_periodic = (total_messages % 5 == 0)
        
        # Only send callback if highly relevant
        if has_fresh_intel or is_periodic:
            background_tasks.add_task(
                callback_service.send_final_result,
                session_id=session_id,
                scam_detected=True,
                total_messages=total_messages,
                intel=response.extractedIntelligence,
                agent_notes=response.agentNotes
            )
        
    else:
        # Not a scam, maybe just normal chatter?
        response.agentResponse = "I'm sorry, I didn't understand that. Who is this?"
        response.agentNotes = "No scam detected yet."

    return response
