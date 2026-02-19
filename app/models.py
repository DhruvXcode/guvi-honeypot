from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any, Dict
from datetime import datetime


# ============================================================================
# Request Models (What GUVI sends us) - Extra flexible for compatibility
# ============================================================================

class Message(BaseModel):
    """Single message in the conversation."""
    model_config = {"extra": "allow"}  # Accept any extra fields GUVI sends
    
    sender: str = Field(default="scammer", description="Either 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Optional[Any] = Field(default=None, description="Timestamp - can be string or int (epoch ms)")


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    model_config = {"extra": "allow"}  # Accept any extra fields
    
    channel: Optional[str] = Field(default="SMS", description="SMS/WhatsApp/Email/Chat")
    language: Optional[str] = Field(default="English", description="Language used")
    locale: Optional[str] = Field(default="IN", description="Country or region")


class HoneypotRequest(BaseModel):
    """Incoming request from GUVI's Mock Scammer API."""
    model_config = {"extra": "allow"}  # Accept any extra fields
    
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current incoming message")
    conversationHistory: Optional[List[Message]] = Field(
        default_factory=list, 
        description="Previous messages in the conversation"
    )
    metadata: Optional[Metadata] = Field(default=None)


# ============================================================================
# Response Models (What we return)
# ============================================================================

class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the scam conversation."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    emailAddresses: List[str] = Field(default_factory=list)
    # New fields from Feb 19 rubric
    caseIds: List[str] = Field(default_factory=list)
    policyNumbers: List[str] = Field(default_factory=list)
    orderNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class EngagementMetrics(BaseModel):
    """Metrics about how long we kept the scammer engaged."""
    engagementDurationSeconds: int = Field(default=0)
    totalMessagesExchanged: int = Field(default=0)


class HoneypotResponse(BaseModel):
    """
    Response sent back to GUVI after processing a message.
    
    Feb 19 Scoring (100 pts total):
    - Scam Detection:        20 pts (scamDetected: true)
    - Intelligence:          30 pts (30 ÷ total_fake_fields per item)
    - Conversation Quality:  30 pts (turns, questions, red flags, elicitation)
    - Engagement Quality:    10 pts (duration + messages)
    - Response Structure:    10 pts (required + optional fields)
    """
    # Required fields (2pts each for sessionId, scamDetected, extractedIntelligence)
    status: str = Field(default="success")
    reply: str = Field(default="", description="The AI agent's reply to the scammer")
    sessionId: Optional[str] = Field(default=None, description="Session ID (2pts structure)")
    scamDetected: bool = Field(default=True, description="Whether a scam was detected (2pts structure)")
    scamType: Optional[str] = Field(default=None, description="Type of scam detected (1pt structure)")
    confidenceLevel: Optional[float] = Field(default=None, description="Confidence 0-1 (1pt structure)")
    extractedIntelligence: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "phoneNumbers": [],
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "emailAddresses": [],
            "caseIds": [],
            "policyNumbers": [],
            "orderNumbers": []
        },
        description="Intelligence extracted from conversation (2pts structure)"
    )
    # Engagement fields (1pt for both together)
    totalMessagesExchanged: Optional[int] = Field(default=None, description="Root-level message count")
    engagementDurationSeconds: Optional[int] = Field(default=None, description="Root-level duration")
    engagementMetrics: Dict[str, int] = Field(
        default_factory=lambda: {
            "totalMessagesExchanged": 0,
            "engagementDurationSeconds": 0
        },
        description="Engagement metrics nested object"
    )
    agentNotes: str = Field(default="", description="Analysis notes for evaluator (1pt structure)")



# ============================================================================
# Internal Models
# ============================================================================

class ScamAnalysis(BaseModel):
    """Result of scam detection analysis."""
    is_scam: bool = Field(default=False)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    detected_patterns: List[str] = Field(default_factory=list)
    reasoning: str = Field(default="")


class ConversationState(BaseModel):
    """Tracks the state of an ongoing conversation."""
    session_id: str
    scam_detected: bool = False
    scam_confidence: float = 0.0
    start_time: Optional[datetime] = None
    message_count: int = 0
    extracted_intelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)
    agent_notes: List[str] = Field(default_factory=list)
