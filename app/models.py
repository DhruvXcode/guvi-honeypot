from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# Request Models (What GUVI sends us)
# ============================================================================

class Message(BaseModel):
    """Single message in the conversation."""
    sender: str = Field(..., description="Either 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    channel: Optional[str] = Field(default="SMS", description="SMS/WhatsApp/Email/Chat")
    language: Optional[str] = Field(default="English", description="Language used")
    locale: Optional[str] = Field(default="IN", description="Country or region")


class HoneypotRequest(BaseModel):
    """Incoming request from GUVI's Mock Scammer API."""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current incoming message")
    conversationHistory: List[Message] = Field(
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
    suspiciousKeywords: List[str] = Field(default_factory=list)


class EngagementMetrics(BaseModel):
    """Metrics about how long we kept the scammer engaged."""
    engagementDurationSeconds: int = Field(default=0)
    totalMessagesExchanged: int = Field(default=0)


class HoneypotResponse(BaseModel):
    """Response sent back to GUVI after processing a message."""
    status: str = Field(default="success")
    scamDetected: bool = Field(default=False)
    agentResponse: str = Field(default="", description="The AI agent's reply to the scammer")
    engagementMetrics: EngagementMetrics = Field(default_factory=EngagementMetrics)
    extractedIntelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)
    agentNotes: str = Field(default="", description="Agent's analysis notes")


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
