"""
Scam Detection Service - GUVI Hackathon Compliant
Handles: Scam vs Legitimate message classification with confidence scoring
"""

import json
import re
import asyncio
import logging
from groq import AsyncGroq
from openai import AsyncOpenAI
from app.config import settings
from app.models import ScamAnalysis, Message
from typing import List, Tuple

logger = logging.getLogger(__name__)

class ScamDetectorService:
    """
    Intelligent scam detection with:
    - Domain whitelisting for legitimate services
    - Automated message detection
    - Confidence thresholding
    - Context-aware analysis
    """

    def __init__(self):
        # Primary: Groq - DISABLE RETRIES to fail fast and switch to Cerebras
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY, max_retries=0)
        self.groq_model = settings.GROQ_MODEL
        
        # Fallback: Cerebras (same Llama 3.3 70B model)
        self.cerebras_client = None
        self.cerebras_model = "qwen-3-235b-a22b-instruct-2507"  # 235B MoE, native Hinglish, same 30 RPM as llama3.1-8b
        if settings.CEREBRAS_API_KEY:
            self.cerebras_client = AsyncOpenAI(
                api_key=settings.CEREBRAS_API_KEY,
                base_url=settings.CEREBRAS_BASE_URL
            )
        
        self._call_counter = 0
        
        # Legitimate domains that reduce scam likelihood
        self.legitimate_domains = {
            # Banking
            "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com",
            "kotak.com", "yesbank.in", "pnb.co.in", "bankofbaroda.in",
            # Insurance
            "hdfclife.com", "hli.app", "licindia.in", "iciciprulife.com",
            "sbigeneral.in", "bajajallianz.com",
            # Government
            "gov.in", "uidai.gov.in", "incometax.gov.in",
            # Telecom
            "jio.com", "airtel.in", "vi.com",
            # E-commerce
            "amazon.in", "flipkart.com", "myntra.com",
            # Payment
            "paytm.com", "phonepe.com", "gpay.in"
        }
        
        # Patterns indicating automated/bulk messages (likely legitimate)
        self.automated_patterns = [
            r"policy\s*no[.:]?\s*\d+",  # Policy numbers
            r"order\s*#?\s*\d+",  # Order numbers
            r"otp\s*is\s*\d{4,6}",  # OTP messages (legit service sending OTP)
            r"delivered\s*on\s*\d{1,2}[-/]\d{1,2}",  # Delivery notifications
            r"your\s*bill\s*(of|for)\s*rs\.?\s*\d+",  # Bill notifications
        ]
        
        # SCAM indicators - strong signals
        self.scam_indicators = [
            r"account\s*(will\s*be\s*)?(blocked|suspended|closed)\s*today",
            r"verify\s*immediately",
            r"click\s*now\s*to\s*avoid",
            r"share\s*(your\s*)?(otp|pin|password)",
            r"won\s*(a\s*)?(lottery|prize|reward)",
            r"unauthorized\s*transaction",
            r"kyc\s*(expir|updat|mandatory)",
            # Additional urgency/coercion patterns
            r"(unblock|re-?activate)\s*(your\s*)?(account|card)",
            r"(share|send)\s*(it\s*)?now",
            r"(share|send)\s*(it\s*)?immediately",
            r"urgent\s*action\s*required",
            r"(account|card)\s*(is\s*)?at\s*risk",
        ]
        
        # Coercive/threatening keywords that override automated classification
        self.coercive_keywords = [
            "unblock", "suspend", "blocked", "share now", "share immediately",
            "urgent", "immediately", "act now", "at risk", "will be closed",
            "verify your", "confirm your identity", "last chance", "final warning"
        ]
        
    def _check_url_legitimacy(self, text: str) -> Tuple[bool, List[str]]:
        """Check if URLs in message are from legitimate sources."""
        urls = re.findall(r"https?://([^\s/]+)", text.lower())
        
        legitimate_urls = []
        suspicious_urls = []
        
        for url in urls:
            # Strip port number if present (e.g., amazon.in:443 -> amazon.in)
            hostname = url.split(":")[0] if ":" in url else url
            
            is_legit = False
            for domain in self.legitimate_domains:
                # Proper suffix match: hostname must END with domain or .domain
                # Prevents spoofing like amazon.in.verify-now.ru
                if hostname == domain or hostname.endswith("." + domain):
                    is_legit = True
                    legitimate_urls.append(url)
                    break
            if not is_legit:
                suspicious_urls.append(url)
        
        # If ALL urls are legitimate, it's likely not a scam
        if urls and not suspicious_urls:
            return True, legitimate_urls
        return False, suspicious_urls
    
    def _is_automated_message(self, text: str) -> bool:
        """Detect if message is automated/bulk (likely legitimate service).
        
        Returns False (not automated) if coercive/threatening language is also
        present, since real automated notifications don't use threats.
        """
        text_lower = text.lower()
        
        # First check: does it look automated?
        is_automated = False
        for pattern in self.automated_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                is_automated = True
                break
        
        if not is_automated:
            return False
        
        # Override: if coercive/threatening language is present, it's NOT automated.
        # Real service notifications (OTP, order, delivery) don't contain threats.
        for keyword in self.coercive_keywords:
            if keyword in text_lower:
                return False
        
        return True
    
    def _has_strong_scam_indicators(self, text: str) -> Tuple[bool, List[str]]:
        """Check for strong scam language patterns."""
        text_lower = text.lower()
        found_patterns = []
        
        for pattern in self.scam_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_patterns.append(pattern.replace("\\s*", " ").replace("\\s+", " "))
        
        return len(found_patterns) > 0, found_patterns

    async def analyze(self, message: str, history: List[Message] = None) -> ScamAnalysis:
        """
        Analyze a message for scam intent with multi-layer detection.
        
        Layer 1: URL legitimacy check
        Layer 2: Automated message detection
        Layer 3: Strong scam indicator patterns
        Layer 4: LLM-based contextual analysis
        """
        if history is None:
            history = []
        
        # ============== LAYER 1: URL CHECK (advisory, does NOT short-circuit) ==============
        urls_legit, url_list = self._check_url_legitimacy(message)
        # Note: Even if URLs are legit, we still check for scam patterns.
        # Scammers can include real bank URLs alongside threatening language.
        
        # ============== LAYER 2: STRONG SCAM INDICATORS (check BEFORE automated) ==============
        has_scam_signals, scam_patterns = self._has_strong_scam_indicators(message)
        if has_scam_signals:
            return ScamAnalysis(
                is_scam=True,
                confidence=0.9,
                detected_patterns=scam_patterns,
                reasoning=f"Strong scam indicators detected: urgency + threat language"
            )
        
        # ============== LAYER 3: AUTOMATED MESSAGE CHECK (only if no scam signals) ==============
        if self._is_automated_message(message):
            return ScamAnalysis(
                is_scam=False,
                confidence=0.75,
                detected_patterns=["automated_notification"],
                reasoning="Message appears to be an automated notification from a service (contains policy/order numbers, OTPs, or delivery info)"
            )
        
        # ============== LAYER 4: LLM CONTEXTUAL ANALYSIS ==============
        # Only call LLM if layers 1-3 are inconclusive
        
        # Build context from history (last 5 messages)
        context_str = ""
        if history:
            context_str = "Previous messages:\n" + "\n".join([
                f"- {msg.sender}: {msg.text}" for msg in history[-5:]
            ])
        
        prompt = f"""You are an expert in detecting financial scams in India.
Analyze this message and determine if it's a SCAM or LEGITIMATE.

MESSAGE: "{message}"
{context_str}

CLASSIFICATION RULES:
1. LEGITIMATE messages:
   - Automated notifications (policy maturity, order delivery, OTP)
   - No immediate threat or urgency
   - Come from known services (banks, insurance, e-commerce)
   - Ask you to visit branch or official website
   
2. SCAM messages:
   - Create artificial urgency ("blocked TODAY", "verify NOW")
   - Ask for sensitive info (OTP, PIN, password) directly
   - Threaten negative consequences if you don't act
   - Contain suspicious links to unknown domains
   - Unsolicited offers (lottery, job, loan approval)

EXAMPLES:
- "Your HDFC policy No.04137874 is maturing on 27-04-2026. Submit documents at your nearest branch." -> LEGITIMATE (no urgency, official process)
- "Your SBI account is blocked! Share OTP 456789 to unblock immediately." -> SCAM (urgency + OTP request)
- "Hi, I am from customer support. Can you share your details?" -> SCAM (unsolicited contact asking for info)
- "Your order #12345 has been delivered. Rate your experience." -> LEGITIMATE (notification, no ask)

Respond in JSON:
{{
    "is_scam": boolean,
    "confidence": float (0.0 to 1.0),
    "reasoning": "brief explanation",
    "detected_patterns": ["list", "of", "signals"]
}}"""

        # Try to get LLM classification with fallback
        text_response = await self._call_llm_for_detection(prompt)
        
        if text_response:
            try:
                result = json.loads(text_response)
                confidence = result.get("confidence", 0.0)
                is_scam = result.get("is_scam", False)
                
                # Apply confidence threshold - only flag if confidence > 0.6
                if is_scam and confidence < 0.6:
                    is_scam = False
                    result["reasoning"] = f"Low confidence ({confidence:.2f}) - treating as non-scam"
                
                return ScamAnalysis(
                    is_scam=is_scam,
                    confidence=confidence,
                    detected_patterns=result.get("detected_patterns", []),
                    reasoning=result.get("reasoning", "")
                )
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
        
        # CRITICAL FIX: On LLM failure, DEFAULT TO SCAM (safer for honeypot)
        # Rationale: In a honeypot, most messages ARE scams. 
        # False positive (engaging with legit person) is better than false negative (not engaging with scammer)
        logger.warning("LLM analysis inconclusive - defaulting to scam for safety")
        return ScamAnalysis(
            is_scam=True, 
            confidence=0.70, 
            detected_patterns=["heuristic_default"],
            reasoning="Analysis inconclusive - treating as potential scam for safety"
        )
    
    async def _call_llm_for_detection(self, prompt: str) -> str:
        """
        Call LLM with round-robin provider selection for scam detection.
        Returns the response text or None if both providers fail.
        """
        self._call_counter += 1
        messages = [
            {"role": "system", "content": "You are a scam detection API. Output JSON only. Be conservative - only flag as scam if confidence > 0.6"},
            {"role": "user", "content": prompt}
        ]
        
        # Round-robin: alternate between providers
        if self.cerebras_client and self._call_counter % 2 == 0:
            providers = [
                ("Cerebras", lambda: self._try_cerebras_detection(messages)),
                ("Groq", lambda: self._try_groq_detection(messages)),
            ]
        else:
            providers = [
                ("Groq", lambda: self._try_groq_detection(messages)),
                ("Cerebras", lambda: self._try_cerebras_detection(messages)),
            ]
        
        for name, try_fn in providers:
            result = await try_fn()
            if result:
                return result
        
        return None
    
    async def _try_groq_detection(self, messages: list) -> str:
        """Attempt Groq API call for scam detection with JSON mode."""
        try:
            response = await asyncio.wait_for(
                self.groq_client.chat.completions.create(
                    messages=messages,
                    model=self.groq_model,
                    response_format={"type": "json_object"},
                    temperature=0.1
                ),
                timeout=8.0
            )
            content = response.choices[0].message.content
            if content:
                return content
        except asyncio.TimeoutError:
            logger.warning("Groq TIMEOUT (>8s) for scam detection")
        except Exception as e:
            logger.warning(f"Groq scam detection error: {type(e).__name__}: {str(e)[:100]}")
        return None
    
    async def _try_cerebras_detection(self, messages: list) -> str:
        """Attempt Cerebras API call for scam detection with JSON extraction."""
        if not self.cerebras_client:
            return None
        try:
            response = await asyncio.wait_for(
                self.cerebras_client.chat.completions.create(
                    messages=messages,
                    model=self.cerebras_model,
                    temperature=0.1,
                    max_tokens=500
                ),
                timeout=10.0
            )
            content = response.choices[0].message.content
            if content:
                # Cerebras may return text before/after JSON - extract it
                json_match = re.search(r'\{[^{}]*"is_scam"[^{}]*\}', content, re.DOTALL)
                if json_match:
                    return json_match.group()
                return content
        except asyncio.TimeoutError:
            logger.warning("Cerebras TIMEOUT (>10s) for scam detection")
        except Exception as e:
            logger.warning(f"Cerebras scam detection error: {type(e).__name__}: {str(e)[:100]}")
        return None

    async def analyze_quick(self, message: str) -> ScamAnalysis:
        """
        Quick analysis using only regex patterns (no LLM call).
        Use for performance optimization when needed.
        """
        # Check scam indicators
        has_scam, patterns = self._has_strong_scam_indicators(message)
        if has_scam:
            return ScamAnalysis(
                is_scam=True,
                confidence=0.85,
                detected_patterns=patterns,
                reasoning="Quick scan: scam patterns detected"
            )
        
        # Check legitimate indicators
        urls_legit, _ = self._check_url_legitimacy(message)
        if urls_legit:
            return ScamAnalysis(
                is_scam=False,
                confidence=0.80,
                detected_patterns=["legitimate_domain"],
                reasoning="Quick scan: legitimate domain detected"
            )
        
        if self._is_automated_message(message):
            return ScamAnalysis(
                is_scam=False,
                confidence=0.75,
                detected_patterns=["automated"],
                reasoning="Quick scan: automated notification pattern"
            )
        
        # Inconclusive
        return ScamAnalysis(
            is_scam=False,
            confidence=0.5,
            detected_patterns=["inconclusive"],
            reasoning="Quick scan: no strong signals either way"
        )
