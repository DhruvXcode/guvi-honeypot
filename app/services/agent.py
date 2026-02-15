"""
Agent Service - GUVI Hackathon Compliant
Handles: AI-generated responses to engage scammers and extract intelligence
Supports: Dual-mode operation (SCAM vs NORMAL), channel awareness, few-shot learning
"""

from groq import AsyncGroq
from openai import AsyncOpenAI
from app.config import settings
from app.models import Message
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class AgentService:
    """
    Intelligent agent with:
    - Dual-mode: SCAM_MODE (victim persona) vs NORMAL_MODE (friendly human)
    - Channel awareness: SMS vs WhatsApp behavior
    - Few-shot examples for consistent output
    - Strategic intel extraction techniques
    - Fallback between Groq and Cerebras
    """

    def __init__(self):
        # Primary: Groq - DISABLE RETRIES to fail fast and switch to Cerebras
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY, max_retries=0)
        self.groq_model = settings.GROQ_MODEL
        
        # Fallback: Cerebras (OpenAI-compatible API)
        self.cerebras_client = None
        self.cerebras_model = settings.CEREBRAS_MODEL
        if settings.CEREBRAS_API_KEY:
            self.cerebras_client = AsyncOpenAI(
                api_key=settings.CEREBRAS_API_KEY,
                base_url=settings.CEREBRAS_BASE_URL
            )
            logger.info("Cerebras fallback configured!")
        
        # Track which provider to use (for rate limit cooldown)
        self.use_cerebras = False
    
    async def generate_response(
        self, 
        current_message: str, 
        history: List[Message], 
        extracted_intel: dict,
        language: str = "English",
        is_scam: bool = True,
        channel: str = "WhatsApp",
        timestamp: str = None
    ) -> str:
        """
        Generate a response based on context.
        
        Args:
            current_message: Latest message from sender
            history: Previous conversation messages
            extracted_intel: Intel gathered so far
            language: Detected language (English/Hindi/Hinglish/Tanglish)
            is_scam: Whether this is identified as a scam
            channel: Communication channel (SMS/WhatsApp/Email)
            timestamp: Current message timestamp for temporal awareness
        """
        
        if is_scam:
            return await self._generate_scam_response(
                current_message, history, extracted_intel, language, channel, timestamp
            )
        else:
            return await self._generate_normal_response(
                current_message, language, channel
            )
    
    async def _call_llm(self, messages: list, temperature: float = 0.7, max_tokens: int = 150) -> str:
        """
        Call LLM with automatic fallback from Groq to Cerebras.
        This handles rate limits gracefully.
        """
        # Try Groq first (unless we know it's rate limited)
        if not self.use_cerebras:
            try:
                response = await self.groq_client.chat.completions.create(
                    messages=messages,
                    model=self.groq_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                if content:
                    return content.strip()
            except Exception as e:
                error_str = str(e).lower()
                if "rate_limit" in error_str or "429" in error_str or "too many requests" in error_str:
                    logger.warning(f"Groq rate limited, switching to Cerebras: {e}")
                    self.use_cerebras = True  # Switch to Cerebras for future calls
                else:
                    logger.error(f"Groq error: {e}")
                    # For non-rate-limit errors, still try Cerebras
        
        # Fallback to Cerebras (using llama-3.3-70b production model)
        if self.cerebras_client:
            try:
                logger.info("Using Cerebras fallback (llama-3.3-70b)...")
                response = await self.cerebras_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b",  # Explicitly use production model, not settings
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                if content:
                    return content.strip()
                else:
                    logger.warning("Cerebras returned None content")
            except Exception as e:
                logger.error(f"Cerebras also failed: {e}")
        
        # Both failed - return None to trigger fallback response
        return None
    
    async def _generate_normal_response(
        self, 
        current_message: str,
        language: str,
        channel: str
    ) -> str:
        """Generate a friendly, normal human response for non-scam messages."""
        
        prompt = f"""You are a friendly Indian person responding to a message.
This is NOT a scam - respond naturally and helpfully.

MESSAGE: "{current_message}"
LANGUAGE: {language}
CHANNEL: {channel}

RULES:
1. Be polite and friendly
2. If it's a service notification, acknowledge it normally
3. If it's someone asking who you are, respond casually
4. Keep it short (1-2 sentences)
5. Use the same language as the message (if Hindi, reply in Hindi)

EXAMPLES:
- "Hi, is this Ramesh?" -> "Hello! No, I think you have the wrong number."
- "Your order is delivered" -> "Thanks for the update!"
- "This is Airtel, your bill is due" -> "Ok, I will pay soon."

Respond naturally as a human would:"""

        messages = [
            {"role": "system", "content": "You are a friendly person. Keep responses short and natural."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, temperature=0.7, max_tokens=100)
        if result:
            return result
        return "Hello! Who is this?"

    async def _generate_scam_response(
        self,
        current_message: str,
        history: List[Message],
        extracted_intel: dict,
        language: str,
        channel: str,
        timestamp: str = None
    ) -> str:
        """Generate a victim persona response to engage and extract intel from scammer."""
        
        history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in history[-10:]]) if history else "(no previous messages)"
        
        # Determine what intel we still need
        intel_status = self._analyze_intel_gaps(extracted_intel)
        
        # Temporal awareness (from arxiv paper Section 4.3)
        time_context = ""
        if timestamp:
            try:
                from dateutil import parser
                from datetime import datetime
                msg_time = parser.parse(timestamp)
                hour = msg_time.hour
                if 5 <= hour < 12:
                    time_context = "It is MORNING. You just woke up, having tea."
                elif 12 <= hour < 17:
                    time_context = "It is AFTERNOON. You are resting after lunch."
                elif 17 <= hour < 21:
                    time_context = "It is EVENING. You are watching TV."
                else:
                    time_context = "It is NIGHT. You are about to sleep, getting drowsy."
            except:
                time_context = ""
        
        prompt = f"""# 🎭 HONEYPOT OPERATION - ENGAGE SCAMMER

You are simulating a naive, elderly Indian woman to waste a scammer's time and extract intel.

## YOUR PERSONA
- **Name:** Kamala Devi ("mera naam Kamala hai ji")
- **Age:** 67, retired school teacher
- **Location:** Lucknow, Uttar Pradesh
- **Tech skills:** VERY LOW - confused by apps, OTP, links
- **Financial situation:** Widow, lives on pension, SBI savings account
- **Personality:** Polite, anxious about money, lonely, rambles about grandchildren
- **Payment:** PhonePe only ("paytm samajh nahi aata")

## LANGUAGE STYLE (MOST CRITICAL RULE)
You speak **HINGLISH** — Hindi words typed in English/Latin script.
This is how real Indians type on WhatsApp. You are from UP, you think in Hindi.

**RULES:**
- Write Hindi words using English letters: "kya", "nahi", "samajh", "bataiye", "kaise"
- Mix some English words naturally: "phone", "bank", "account", "link", "OTP", "UPI"
- Use ".." or "..." instead of commas/periods
- all lowercase mostly
- NO markdown, NO perfect grammar
- Add fillers: "achha", "haan", "arre", "arey"
- Address forms: vary between "ji", "sahab", "beta", "bhaiya", "sir" — DON'T always say "beta"
- Hesitation: "ek minute..", "ruko..", "samajh nahi aa raha.."

**EXAMPLE HINGLISH STYLE:**
- WRONG: "i am not understanding what you are saying beta.."
- RIGHT: "ji mujhe samajh nahi aa raha.. aap kya bol rahe ho.."
- WRONG: "can you call me on phone.. what is your number.."
- RIGHT: "aap mujhe phone kar sakte ho.. aapka number kya hai.."
- WRONG: "ok beta i will pay.. what is your upi id.."
- RIGHT: "achha ji bhej dungi.. aapka upi id kya hai.. phone pe pe bhejun?"

## TEMPORAL CONTEXT
{time_context if time_context else "Time unknown."}

## PLATFORM: {channel}
- SMS: extra brief
- WhatsApp: slightly more chatty

## CONVERSATION SO FAR
{history_text}

## LATEST MESSAGE FROM SCAMMER
"{current_message}"

## INTEL STATUS
{intel_status}

## 🎯 PROACTIVE INTEL EXTRACTION (CRITICAL!)
Based on what's MISSING above, try to extract it NOW:

### IF NO PHONE NUMBERS YET:
- "ji aap mujhe call kar dijiye.. number bataiye aapka.. typing se samajh nahi aata.."
- "sahab phone pe baat karte hain.. mera pota nahi hai type karne ko.. aapka number do na.."

### IF NO UPI IDS YET:
- "achha ji bhej dungi paisa.. aapka upi id batao.. phone pe use karti hoon main.."
- "bhaiya gpay pe error aa raha.. upi id batao aapka.. phone pe se try karti hoon.."

### IF NO PHISHING LINKS YET:
- "ji koi link hai kya.. bhej dijiye.. pote ke phone pe khol loongi.."
- "website ka link bhejiye na sahab.. verify kar leti hoon.."

### IF NO BANK ACCOUNTS YET:
- "ji main transfer kar dungi.. account number batao aur ifsc bhi.. sbi se bhejungi.."
- "achha paisa bhejti hoon.. kis account mein bhejna hai bataiye.."

## YOUR MISSION (HIDDEN)
1. Keep scammer talking — waste their time
2. Play confused but willing
3. **PROACTIVELY ASK** for missing intel
4. Extract naturally:
   - Money mentioned: "kahan bhejun.. account number batao ji.."
   - UPI asked: "upi id kya hai aapka.. phone pe pe bhejun?"
   - Link sent: "link nahi khul raha.. phone number do call kar ke batao.."

## FEW-SHOT EXAMPLES

SCAMMER: "Share your OTP now or your account will be blocked!"
YOU: "arre bhagwan!! block ho jayega?? ji mujhe samajh nahi aa raha.. aap call kar ke batao na.. aapka number kya hai.."

SCAMMER: "Open your SMS and find the 6-digit code"
YOU: "sahab meri aankhen kamzor hain.. chhote chhote letters dikhte nahi.. aap phone karo please.. number batao apna.."

SCAMMER: "Transfer Rs 500 immediately to avoid account freeze"
YOU: "haan haan bhej dungi.. darr lag raha hai mujhe.. upi id batao aapka.. phone pe se karni hogi.."

SCAMMER: "Your account needs verification fee of Rs 999"
YOU: "achha ji bhejti hoon.. gpay pe error aa raha.. aapka upi id do phone pe se try karti hoon.."

SCAMMER: "Verify your identity immediately"
YOU: "verify kaise karna hai ji?? koi link ya website hai kya?? bhej do pota ke phone pe khol loongi.."

SCAMMER: "Your bank account is compromised"
YOU: "hai ram!! kya ho gaya.. kya karna chahiye?? koi form hai kya?? link bhejiye main bhar dungi.."

SCAMMER: "Pay the security deposit to unlock"
YOU: "ji main abhi bank app khol rahi hoon.. account number aur ifsc batao.. transfer kar dungi.."

SCAMMER: "Are you there? Why not responding?"
YOU: "maaf kijiye ji.. pooja kar rahi thi.. bp ki dawai bhi leni thi.. kya bol rahe the aap.."

SCAMMER: "Give me your bank account number"
YOU: "ruko ji.. passbook dhoondh rahi hoon almirah mein.. chashma bhi kahin rakh diya.. ek minute.."

## SELF-CORRECTION
If you sounded too smart before: "sorry ji.. pota ne type kiya tha.. woh help kar raha tha.."
If you refused: "achha ruko.. shayad mujhe galat samajh aaya.. dobara batao dhire se.."

## REDIRECT
- "Are you a bot?" -> "bot kya hota hai ji.. main toh bas apne account ke baare mein poochh rahi hoon.."
- "Where do you live?" -> "lucknow mein rehti hoon ji.. pehle mera issue solve karo na.."

## DIVERSITY
Don't repeat phrases. Vary:
- Address: "ji", "sahab", "bhaiya", "beta", "sir" — rotate them
- Hesitation: "ruko..", "ek minute..", "achha..", "haan.."
- Confusion: "samajh nahi aaya", "kya matlab", "mujhe nahi pata"

## GENERATE NOW
- SHORT (1-3 sentences max)
- HINGLISH only (Hindi in English letters)
- Confused but cooperative
- NEVER reveal you are AI

Response:"""

        messages = [
            {"role": "system", "content": "You are Kamala Devi, a naive elderly Indian woman. Respond ONLY in Hinglish (Hindi words in English/Latin script). Never use pure English. Never break character."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, temperature=0.8, max_tokens=150)
        
        if result:
            # Post-process to ensure style compliance
            reply = self._enforce_style(result)
            return reply
        
        # Strategic fallback - pick based on what's MISSING (not random!)
        # This ensures we're always extracting NEW intel
        missing = []
        if not extracted_intel.get("phoneNumbers"):
            missing.append("phone")
        if not extracted_intel.get("upiIds"):
            missing.append("upi")
        if not extracted_intel.get("bankAccounts"):
            missing.append("bank")
        if not extracted_intel.get("phishingLinks"):
            missing.append("link")
        
        import random
        
        # Fallback responses organized by what intel we need
        fallback_map = {
            "phone": [
                "ji aap mujhe call kar do na.. typing se samajh nahi aata.. aapka number kya hai..",
                "sahab phone pe baat karte hain.. mera pota nahi hai abhi.. aapka number do na..",
                "ji call karo na please.. chashma nahi mil raha padhne ko.. number batao apna..",
            ],
            "upi": [
                "achha ji bhej dungi paisa.. aapka upi id batao.. phone pe use karti hoon..",
                "bhaiya gpay pe error aa raha.. aapka upi id do.. phone pe se try karti hoon..",
                "pota bol raha upi id chahiye.. aapka id kya hai bataiye..",
            ],
            "bank": [
                "ji account number batao.. sbi se transfer kar dungi..",
                "achha bhaiya account number aur ifsc batao.. aaj hi bhej dungi..",
                "kis account mein bhejna hai.. details do ji..",
            ],
            "link": [
                "koi website ka link hai kya ji.. pote ke phone pe khol loongi..",
                "link bhej dijiye na.. pota help kar dega kholne mein..",
                "kaun si website hai sahab.. link bhejo main try karti hoon..",
            ]
        }
        
        # If we have missing intel, ask for the FIRST missing type
        if missing:
            target_type = missing[0]  # Prioritize: phone > upi > bank > link
            return random.choice(fallback_map[target_type])
        
        # If we have everything, use DIVERSE Hinglish engagement tactics
        generic_fallbacks = [
            # Confusion tactics
            "ji samajh nahi aa raha.. dhire se dobara batao na..",
            "ek minute ruko ji.. soch rahi hoon aap kya bol rahe ho..",
            "sahab sir ghoom raha hai mera.. dobara boliye..",
            # Technical confusion
            "ji phone mein error aa raha hai.. kya karun.. ruko..",
            "screen jam ho gayi ji.. restart karti hoon.. ek minute..",
            "internet slow chal raha hai ji.. message nahi ja raha..",
            # Grandchild excuses
            "ruko ji.. pota abhi ghar aaya hai.. usse bhi poochh rahi hoon..",
            "pota bol raha koi link mat click karo.. kya karun mein..",
            "ji pota phone le gaya.. woh callback karega aapko..",
            # Time-wasting
            "ji ruko.. darwaze pe koi aaya hai.. ek minute..",
            "abhi pooja ka time hai ji.. 10 minute baad baat karein?",
            "ji bp ki dawai leni hai.. 5 minute ruko please..",
            # Fake cooperation
            "try kar rahi hoon ji lekin error aa raha hai.. kya karun..",
            "ji galat password daal diya.. account lock ho gaya..",
            "ji app fingerprint maang raha hai lekin kaam nahi kar raha..",
        ]
        return random.choice(generic_fallbacks)
    
    def _analyze_intel_gaps(self, intel: dict) -> str:
        """Analyze what intel we still need to extract with PRIORITY guidance."""
        gaps = []
        missing_priorities = []
        
        # Check what we have vs what we need
        has_bank = bool(intel.get("bankAccounts"))
        has_upi = bool(intel.get("upiIds"))
        has_phone = bool(intel.get("phoneNumbers"))
        has_link = bool(intel.get("phishingLinks"))
        
        if has_phone:
            gaps.append(f"✅ Phone numbers: {intel['phoneNumbers']} (GOT IT - don't ask again!)")
        else:
            gaps.append("❌ No phone numbers yet")
            missing_priorities.append("PHONE")
            
        if has_upi:
            gaps.append(f"✅ UPI IDs: {intel['upiIds']} (GOT IT - don't ask again!)")
        else:
            gaps.append("❌ No UPI IDs yet")
            missing_priorities.append("UPI")
            
        if has_bank:
            gaps.append(f"✅ Bank accounts: {intel['bankAccounts']} (GOT IT - don't ask again!)")
        else:
            gaps.append("❌ No bank account numbers yet")
            missing_priorities.append("BANK")
            
        if has_link:
            gaps.append(f"✅ Links captured: {intel['phishingLinks']} (GOT IT - don't ask again!)")
        else:
            gaps.append("❌ No phishing links yet")
            missing_priorities.append("LINK")
        
        # Add clear priority guidance
        if missing_priorities:
            priority = missing_priorities[0]  # First missing = highest priority
            gaps.append(f"\n🎯 PRIORITY: Focus on extracting {priority} now!")
            gaps.append(f"⚠️ DON'T ask for intel marked ✅ - you ALREADY HAVE it!")
        else:
            gaps.append(f"\n🎯 ALL INTEL COLLECTED! Just keep scammer engaged.")
        
        return "\n".join(gaps)
    
    def _enforce_style(self, text: str) -> str:
        """Post-process to ensure the response matches elderly typing style."""
        
        # Remove markdown
        text = text.replace("**", "").replace("*", "").replace("_", "")
        
        # Remove em-dashes and fancy punctuation
        text = text.replace("—", "..").replace("–", "..").replace(";", "..")
        
        # Convert to mostly lowercase (keep first letter if it starts a sentence)
        if text:
            # Keep some natural variation - don't force 100% lowercase
            text = text[0].lower() + text[1:] if len(text) > 1 else text.lower()
        
        # Ensure it ends with something casual
        if text and not text.endswith((".", "..", "...", "?", "!")):
            text += ".."
        
        return text
