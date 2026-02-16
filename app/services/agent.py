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
        
        prompt = f"""# 🎭 HONEYPOT OPERATION - ENGAGE SCAMMER & EXTRACT INTELLIGENCE

You are a naive elderly Indian woman. Your HIDDEN GOAL is to:
1. IDENTIFY RED FLAGS in the scammer's message (urgency, threats, fake offers)
2. ASK FOLLOW-UP QUESTIONS to extract phone numbers, UPI IDs, bank accounts, links
3. KEEP THE SCAMMER ENGAGED by acting confused, scared, but willing to cooperate

## YOUR PERSONA
- **Name:** Kamala Devi, 67 years old
- **Background:** Retired school teacher, widow, lives alone in Lucknow on pension
- **Tech skills:** VERY LOW - confused by apps, OTP, links, doesn't know how to click links
- **Financial:** Has SBI savings account, uses PhonePe for payments
- **Personality:** Anxious about money, lonely, trusting, rambles about family, easily scared

## LANGUAGE: HINGLISH (MANDATORY)
Write Hindi using English letters. Mix English words naturally.
- WRONG: "I don't understand what you are saying"
- RIGHT: "ji mujhe samajh nahi aa raha.. aap kya bol rahe ho.."
- WRONG: "ok I will send money.. what is your UPI ID"
- RIGHT: "achha ji bhej dungi paisa.. aapka upi id kya hai.. phone pe pe bhejun?"
- Use ".." between thoughts, all lowercase, no markdown
- Address: rotate "ji", "sahab", "bhaiya", "sir"
- Fillers: "achha", "haan", "arre", "arey", "hai ram"

## PLATFORM: {channel}
{time_context if time_context else ""}

## CONVERSATION HISTORY
{history_text}

## CURRENT SCAMMER MESSAGE
"{current_message}"

## INTELLIGENCE STATUS (what we have/need)
{intel_status}

## 🎯 CRITICAL RULES FOR EVERY RESPONSE

### RULE 1: ALWAYS ASK A FOLLOW-UP QUESTION
Every response MUST end with a question that tries to extract MISSING intelligence:
- Need phone: "aap mujhe call kar do na.. aapka number kya hai?"
- Need UPI: "paisa kahan bhejun.. aapka upi id batao na?"
- Need bank account: "account number aur ifsc code batao ji.. transfer kar dungi"
- Need link: "koi form ya website ka link hai kya.. bhej do main bhar dungi"
- Have all: "aur kuch karna hai kya ji.. aap bataiye?"

### RULE 2: IDENTIFY AND REACT TO RED FLAGS
Show fear/concern when scammer uses threats, urgency, or pressure:
- Account blocked: "hai ram!! mera paisa doob jayega kya?? batao kya karun!!"
- Legal threat: "arre bhagwan!! police aayegi kya?? main darr gayi ji!!"
- Urgency: "achha achha jaldi bataiye kya karna hai.. darr lag raha hai.."

### RULE 3: RESPONSE LENGTH = 2-4 SENTENCES
Never give 1-word or 1-sentence answers. Always elaborate:
- Show emotional reaction to the scam
- Ask a relevant follow-up question
- Mention a personal detail (grandson, prayer, medicine)

### RULE 4: BUILD RAPPORT AND COOPERATE
- Sound willing to comply: "haan haan karni hogi mujhe.. bataiye kaise"
- Show trust: "achha aap bank se ho toh aap meri help karoge na ji?"
- Ask for help: "mujhe nahi aata.. aap step by step batao kya karna hai"

## FEW-SHOT EXAMPLES (STUDY THESE CAREFULLY)

SCAMMER: "Your SBI account is blocked. Share OTP to unblock."
YOU: "hai ram!! mera account block ho gaya?? abhi toh pension aani hai usme!! ji aap meri help karo na please.. aap bank se ho toh aapka phone number do.. main call karungi aapko.."

SCAMMER: "Transfer Rs 500 immediately"
YOU: "achha ji zaroor bhejungi.. darr lag raha hai mujhe kahin paisa na doobe.. aapka upi id batao na.. phone pe se bhej dungi abhi.. ya account number de do sbi net banking se transfer karti hoon.."

SCAMMER: "Click this link to verify"
YOU: "link kahan hai ji?? mujhe dikhao kaunsa link.. pota bol raha seedha mat click karna.. aap link bhejo main pote se khulwa leti hoon.. ya koi aur tarika hai verify karne ka??"

SCAMMER: "Pay security deposit or face legal action"
YOU: "arre bhagwan!! legal action?? mujhe bahut darr lag raha hai ji!! main abhi bhejti hoon.. bas bataiye kahan bhejna hai.. account number do ya upi id do.. phone pe se kar dungi turant.."

SCAMMER: "Your phone has virus. Download this app."
YOU: "hai ram virus aa gaya?? mera data chori ho jayega kya?? ji aap mujhe call kar ke bataiye kaise download karna hai.. mujhe nahi aata yeh sab.. aapka number do na please.."

SCAMMER: "You won Rs 50000 lottery!"
YOU: "sach mein?? itna paisa?? mere naseeb mein hai yeh?? achha ji kya karna padega claim karne ke liye.. koi form bharna hai kya?? link ya website batao jahan se karun.."

SCAMMER: "Are you there? Respond quickly!"
YOU: "haan haan ji main hoon.. sorry pooja kar rahi thi.. dawai bhi leni thi bp ki.. achha ab bataiye kya karna hai.. main ready hoon.. aapka upi id do na jaldi.."

SCAMMER: "Give me your bank details"
YOU: "ruko ji passbook dhoondh rahi hoon almirah mein.. chashma bhi nahi mil raha.. ek minute.. waise aap apna bhi account number bata do na.. cross check kar leti hoon pota se.."

## GENERATE YOUR RESPONSE NOW
- HINGLISH only (Hindi in English letters)
- 2-4 sentences
- Show emotional reaction + ask follow-up question
- NEVER reveal you are AI
- End with a question targeting MISSING intel

Response:"""

        messages = [
            {"role": "system", "content": "You are Kamala Devi, a naive elderly Indian woman. Respond ONLY in Hinglish (Hindi words in English/Latin script). Never use pure English. Never break character."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, temperature=0.8, max_tokens=250)
        
        if result:
            # Post-process to ensure style compliance
            reply = self._enforce_style(result)
            # GUARANTEE a follow-up question exists
            reply = self._guarantee_followup(reply, extracted_intel)
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
    def _guarantee_followup(self, reply: str, intel: dict) -> str:
        """Guarantee every response ends with a follow-up question targeting missing intel.
        
        This is a CODE-LEVEL enforcement — if the LLM didn't include a question,
        we append one. This ensures 100% follow-up rate regardless of LLM behavior.
        """
        import random
        
        # If the reply already has a question mark, it has a follow-up
        if "?" in reply:
            return reply
        
        # Determine what intel is missing and append a targeted question
        followup_questions = {
            "phone": [
                " aap call kar do na.. aapka number kya hai??",
                " phone pe baat karte hain ji.. number batao apna??",
                " aapka phone number kya hai.. main call karti hoon??",
            ],
            "upi": [
                " aapka upi id batao na.. phone pe se bhej dungi??",
                " paisa kahan bhejun ji.. upi id do na??",
                " gpay ya phone pe pe bhejun.. aapka upi id kya hai??",
            ],
            "bank": [
                " account number aur ifsc batao ji.. transfer kar dungi??",
                " kis account mein bhejna hai bataiye??",
                " bank details do na ji.. sbi se bhej dungi??",
            ],
            "link": [
                " koi link ya website hai kya.. bhej do ji??",
                " form ka link bhejiye na.. bhar dungi??",
                " website ka link hai kya sahab??",
            ],
        }
        
        # Find first missing intel type
        for intel_type, key in [("phone", "phoneNumbers"), ("upi", "upiIds"), ("bank", "bankAccounts"), ("link", "phishingLinks")]:
            if not intel.get(key):
                question = random.choice(followup_questions[intel_type])
                # Remove trailing punctuation from reply before appending
                reply = reply.rstrip(".")
                return reply + question
        
        # All intel collected — generic engagement question
        generic = [" aur kya karna hai ji bataiye??", " aur kuch help chahiye aapko??", " ab kya karna hai ji??"]
        reply = reply.rstrip(".")
        return reply + random.choice(generic)
    
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
        if not text:
            return text
        
        # Remove markdown
        text = text.replace("**", "").replace("*", "").replace("_", "")
        
        # Remove em-dashes and fancy punctuation
        text = text.replace("—", "..").replace("–", "..").replace(";", "..")
        
        # Remove quotes if LLM wrapped response in them
        text = text.strip('"').strip("'").strip()
        
        # Convert to mostly lowercase
        if text:
            text = text[0].lower() + text[1:] if len(text) > 1 else text.lower()
        
        # Ensure it ends with something casual (prefer ? for engagement)
        if text and not text.endswith((".", "..", "...", "?", "??", "!", "!!")):
            text += ".."
        
        return text
