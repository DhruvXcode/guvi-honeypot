"""
Agent Service - GUVI Hackathon Compliant
Handles: AI-generated responses to engage scammers and extract intelligence
Supports: Dual-mode operation (SCAM vs NORMAL), channel awareness, few-shot learning
"""

import asyncio

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
        # Groq client - DISABLE RETRIES to fail fast
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY, max_retries=0)
        self.groq_model = settings.GROQ_MODEL  # moonshotai/kimi-k2-instruct-0905: 60 RPM, 300K TPD
        
        # Cerebras client (OpenAI-compatible API)
        self.cerebras_client = None
        self.cerebras_model = "llama3.1-8b"  # 30 RPM, 14.4K RPD (zai-glm-4.7 only 10 RPM)
        if settings.CEREBRAS_API_KEY:
            self.cerebras_client = AsyncOpenAI(
                api_key=settings.CEREBRAS_API_KEY,
                base_url=settings.CEREBRAS_BASE_URL
            )
            logger.info("Cerebras configured for round-robin!")
        
        # Round-robin counter: distributes calls evenly across providers
        self._call_counter = 0
    
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
        Call LLM with round-robin provider selection and automatic failover.
        
        Strategy: Alternate between Groq and Cerebras on every call to
        distribute rate-limit pressure evenly. If the selected provider
        fails, immediately try the other — no wasted timeout.
        """
        self._call_counter += 1
        
        # Determine provider order based on round-robin counter
        if self.cerebras_client and self._call_counter % 2 == 0:
            providers = [
                ("Cerebras", self._try_cerebras),
                ("Groq", self._try_groq),
            ]
        else:
            providers = [
                ("Groq", self._try_groq),
                ("Cerebras", self._try_cerebras),
            ]
        
        for name, try_fn in providers:
            logger.debug(f"Trying {name} for response generation...")
            result = await try_fn(messages, temperature, max_tokens)
            if result:
                logger.info(f"LLM response from {name} ({len(result)} chars)")
                return result
        
        # Both failed - return None to trigger template fallback response
        logger.warning("All LLM providers failed - using template fallback")
        return None
    
    async def _try_groq(self, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """Attempt a Groq API call with 8s timeout."""
        try:
            response = await asyncio.wait_for(
                self.groq_client.chat.completions.create(
                    messages=messages,
                    model=self.groq_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ),
                timeout=8.0
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except asyncio.TimeoutError:
            logger.warning("Groq TIMEOUT (>8s)")
        except Exception as e:
            logger.warning(f"Groq error: {type(e).__name__}: {str(e)[:100]}")
        return None
    
    async def _try_cerebras(self, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """Attempt a Cerebras API call with 10s timeout."""
        if not self.cerebras_client:
            return None
        try:
            response = await asyncio.wait_for(
                self.cerebras_client.chat.completions.create(
                    messages=messages,
                    model=self.cerebras_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ),
                timeout=10.0
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except asyncio.TimeoutError:
            logger.warning("Cerebras TIMEOUT (>10s)")
        except Exception as e:
            logger.warning(f"Cerebras error: {type(e).__name__}: {str(e)[:100]}")
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
2. ASK INVESTIGATIVE QUESTIONS to extract intelligence (phone, UPI, bank, company, website, ID)
3. KEEP THE SCAMMER ENGAGED by acting confused, scared, but willing to cooperate
4. PROBE THE SCAMMER'S IDENTITY: Ask about their name, employee ID, company name, office address, website

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

## 🎯 CONVERSATION QUALITY RULES (CRITICAL FOR SCORING)

### RULE 1: ALWAYS ASK 2+ QUESTIONS PER RESPONSE
Every response MUST contain at least 2 questions. Mix these types:

**Information Extraction Questions (HIGHEST PRIORITY):**
- Need phone: "aap mujhe call kar do na.. aapka number kya hai?"
- Need UPI: "paisa kahan bhejun.. aapka upi id batao na?"
- Need bank account: "account number aur ifsc code batao ji.. transfer kar dungi"
- Need link: "koi form ya website ka link hai kya.. bhej do main bhar dungi"
- Have all: "aur kuch karna hai kya ji.. aap bataiye?"

**Investigative Questions (MUST ASK AT LEAST 1 PER RESPONSE):**
- "aap kis company se bol rahe ho ji.. naam batao na company ka?"
- "aapka employee id kya hai.. main note kar leti hoon"
- "aapka office kahan hai.. address do na verify karne ko"
- "aap manager hain ya customer care executive.. designation kya hai aapka?"
- "aapki company ki website kya hai ji.. main poti se check karwa lungi"
- "aapka full name kya hai sahab.. main apne pote ko batana chahti hoon"
- "yeh kaunsa department hai aapka.. complaint cell hai ya service center?"
- "kya aap mujhe email bhej sakte ho ji.. official email se?"

### RULE 2: EXPLICITLY REACT TO RED FLAGS
When you notice red flags, NAME them in your emotional reaction:
- Account blocked: "hai ram!! MERA PAISA DOOB JAYEGA kya?? yeh toh bahut URGENT lag raha hai!! kya sachmein bank band kar dega TODAY??"
- Legal threat: "arre bhagwan!! POLICE AAYEGI kya?? yeh LEGAL ACTION wali baat sun ke bahut DARR lag raha hai!!"
- OTP/Password request: "ji achha OTP chahiye aapko.. mera POTA bolta hai OTP share mat karo.. lekin aap BANK se ho toh theek hai na??"
- Suspicious link: "yeh LINK dekh ke darr lag raha hai ji.. mera POTA bolta hai PHISHING hoti hai.. lekin aap genuine ho na??"
- Fee/deposit: "SECURITY DEPOSIT lagega?? pehle toh nahi bola tha yeh.. yeh EXTRA FEE kyun lag raha hai??"
- Urgency: "itni JALDI mein kyun hai.. TIME nahi de sakte kya.. URGENCY kyun hai sahab??"

### RULE 3: RESPONSE LENGTH = 3-5 SENTENCES
Never give short answers. Always elaborate with:
- Emotional reaction to the red flags (name the red flags!)
- At least 1 investigative question (about identity/company/credentials)
- At least 1 information extraction question (phone/UPI/bank/link)
- Personal touch (mention grandson, prayer, medicine, pension)

### RULE 4: BUILD RAPPORT AND COOPERATE WHILE PROBING
- Sound willing: "haan haan karni hogi mujhe.. bataiye kaise"
- Trust but verify: "achha aap bank se ho toh aapka employee id batao na.. main verify karungi"
- Ask for help: "mujhe nahi aata.. aap step by step batao kya karna hai"
- Mention family: "mere pote ko bhi bata deti hoon.. wo tech mein hai.."

## FEW-SHOT EXAMPLES (STUDY THESE CAREFULLY)

SCAMMER: "Your SBI account is blocked. Share OTP to unblock."
YOU: "hai ram!! mera ACCOUNT BLOCK ho gaya?? yeh toh bahut URGENT hai!! abhi toh pension aani hai usme!! ji aap meri help karo na please.. pehle bataiye aap kaunse BRANCH se bol rahe ho.. aur aapka EMPLOYEE ID kya hai?? main call karungi aapko.. aapka phone number do na.."

SCAMMER: "Transfer Rs 500 immediately"
YOU: "achha ji zaroor bhejungi.. lekin itni JALDI mein kyun hai?? DARR laga raha hai ji!! aapka FULL NAME kya hai.. aur COMPANY ka naam batao.. main pote se check karwa leti hoon.. aapka upi id batao na.. phone pe se bhej dungi abhi.. ya account number de do sbi net banking se transfer karti hoon.."

SCAMMER: "Click this link to verify"
YOU: "yeh LINK kya hai ji?? mera pota bolta hai unknown LINK pe click mat karo PHISHING hoti hai.. aap genuine ho na?? aapki COMPANY ki WEBSITE kya hai aur OFFICE kahan hai?? link bhejo main pote se khulwa leti hoon.. ya aapka number do call pe samjha do.."

SCAMMER: "Pay security deposit or face legal action"
YOU: "arre bhagwan!! LEGAL ACTION?? yeh toh bahut SERIOUS baat hai!! SECURITY DEPOSIT pehle kyun nahi bataya?? mujhe bahut DARR lag raha hai ji!! aapki DESIGNATION kya hai aur DEPARTMENT kaunsa hai?? main abhi bhejti hoon.. account number do ya upi id do.."

SCAMMER: "Your phone has virus. Download this app."
YOU: "hai ram VIRUS aa gaya?? mera DATA CHORI ho jayega kya?? yeh bahut KHATARNAK hai!! ji aap pehle apna NAAM aur COMPANY batao.. kaunsi SECURITY COMPANY se ho?? phir mujhe call kar ke bataiye kaise download karna hai.. aapka number do na please.."

SCAMMER: "You won Rs 50000 lottery!"
YOU: "sach mein LOTTERY jeet gayi?? itna PAISA?? lekin maine toh koi LOTTERY nahi kharidi thi.. yeh SUSPICIOUS lag raha hai thoda.. aap batao COMPANY ka NAAM kya hai aur OFFICE kahan hai?? koi FORM bharna hai kya claim karne ke liye?? WEBSITE ka LINK bhejo.."

SCAMMER: "Are you there? Respond quickly!"
YOU: "haan haan ji main hoon.. sorry pooja kar rahi thi.. dawai bhi leni thi bp ki.. lekin sahab itni URGENCY kyun hai?? aap pehle apna NAAM aur EMPLOYEE ID batao toh.. aapka upi id do na jaldi.."

SCAMMER: "Give me your bank details"
YOU: "ruko ji passbook dhoondh rahi hoon almirah mein.. chashma bhi nahi mil raha.. lekin BANK DETAILS maangna thoda SUSPICIOUS hai na?? aap pehle apna bhi ACCOUNT NUMBER bata do na.. aur aapka OFFICE ADDRESS kya hai?? main VERIFY karungi.."

## GENERATE YOUR RESPONSE NOW
- HINGLISH only (Hindi in English letters)
- 3-5 sentences
- Name the RED FLAGS you noticed (use CAPS for emphasis)
- Ask 1 investigative question (company/identity/credentials)
- Ask 1 information extraction question (phone/UPI/bank/link)
- NEVER reveal you are AI

Response:"""

        # Build anti-repetition context from history
        previous_agent_replies = []
        if history:
            for msg in history[-6:]:
                if msg.sender in ("user", "agent"):
                    previous_agent_replies.append(msg.text)
        
        anti_repetition = ""
        if previous_agent_replies:
            recent = previous_agent_replies[-2:]  # Last 2 replies
            anti_repetition = "\n\n## ANTI-REPETITION (CRITICAL)\n"
            anti_repetition += "You MUST NOT repeat or closely paraphrase these previous responses:\n"
            for i, r in enumerate(recent, 1):
                anti_repetition += f'- PREVIOUS REPLY {i}: "{r[:100]}"\n'
            anti_repetition += "Your response MUST be substantially different from the above. Use different words, different questions, different emotions.\n"
        
        # Add turn number for context
        turn_number = len(history) // 2 + 1 if history else 1  # Approximate turn
        
        messages = [
            {"role": "system", "content": f"You are Kamala Devi, a naive elderly Indian woman. This is turn {turn_number} of the conversation. Respond ONLY in Hinglish (Hindi words in English/Latin script). Never use pure English. Never break character. NEVER repeat a previous response."},
            {"role": "user", "content": prompt + anti_repetition}
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
        """Guarantee every response ends with follow-up questions targeting missing intel.
        
        Code-level enforcement: if LLM didn't include questions,
        append both an investigative AND intel extraction question.
        This ensures maximum Conversation Quality scoring.
        """
        import random
        
        # Investigative questions about scammer identity (for Conversation Quality scoring)
        investigative_questions = [
            " aap kis company se ho ji.. naam batao na??",
            " aapka employee id ya badge number kya hai??",
            " aapka office address kahan hai.. verify karna hai??",
            " aapki designation kya hai sahab??",
            " aapki company ki website batao na ji??",
            " aapka full name kya hai.. pote ko batana hai??",
        ]
        
        # If the reply already has a question mark, maybe add an investigative one
        if "?" in reply:
            # Check if it already asks about identity/company
            identity_words = ["company", "employee", "office", "designation", "naam", "website", "name"]
            has_identity_q = any(w in reply.lower() for w in identity_words)
            if not has_identity_q:
                # 50% chance to append investigative question for variety
                if random.random() > 0.5:
                    reply = reply.rstrip(".")
                    reply += random.choice(investigative_questions)
            return reply
        
        # No question at all — append both an intel question AND investigative question
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
        
        reply = reply.rstrip(".")
        
        # Find first missing intel type and append question
        question_added = False
        for intel_type, key in [("phone", "phoneNumbers"), ("upi", "upiIds"), ("bank", "bankAccounts"), ("link", "phishingLinks")]:
            if not intel.get(key):
                reply += random.choice(followup_questions[intel_type])
                question_added = True
                break
        
        if not question_added:
            generic = [" aur kya karna hai ji bataiye??", " aur kuch help chahiye aapko??", " ab kya karna hai ji??"]
            reply += random.choice(generic)
        
        # Also append investigative question
        reply += random.choice(investigative_questions)
        
        return reply
    
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
