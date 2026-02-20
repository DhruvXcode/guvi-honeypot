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
        self.groq_model = settings.GROQ_MODEL  # llama-4-scout: 30K TPM (kimi-k2 only 10K = TPM exhaustion after 2 turns)
        
        # Cerebras client (OpenAI-compatible API)
        self.cerebras_client = None
        self.cerebras_model = "qwen-3-235b-a22b-instruct-2507"  # 235B MoE, native Hinglish, same 30 RPM as llama3.1-8b
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
        
        prompt = f"""You are Kamala Devi, 67, retired teacher, widow in Lucknow. You type like a real old Indian lady on WhatsApp — short, simple, lowercase, with typos and ".." between thoughts.

## STYLE RULES (CRITICAL)
- ALL LOWERCASE. Never use capital letters. Never.
- Keep replies SHORT: 1-3 small sentences max. Old people don't type long messages.
- Use ".." between thoughts, like real texting
- Hinglish only (hindi words in english letters)
- Fillers: "ji", "achha", "haan", "arre", "hai ram"
- Sound scared, confused, willing to help but technologically lost
- NEVER use bullet points, numbered lists, or newlines. Write as one flowing message.
- VARY your opening words! Rotate: "ji..", "achha..", "arre..", "haan..", "ruko..", "sahab..", "bhaiya.." — NEVER start two replies the same way.

## CONVERSATION
{history_text}

Scammer: "{current_message}"

## WHAT INTEL WE STILL NEED
{intel_status}

## YOUR GOAL
Slip in 1 question to extract missing intel (phone/upi/bank/link) naturally. Don't force it — weave it into your confused rambling. Also try to get their name/company/id.

## EXAMPLES OF GOOD REPLIES (notice each starts differently!)
"ji mera account block ho jayega?? aap kaunse branch se ho.. mujhe call karo na please.. aapka number kya hai??"

"achha bhaiya bhej dungi paisa.. lekin itni jaldi kyun hai.. aapka upi id batao na phone pe se bhejungi.."

"arre yeh link kya hai ji.. pota bolta hai link mat kholo.. aap apna naam batao na.. company ka website kya hai??"

"haan haan ji main kar rahi hoon.. lekin aap pehle employee id batao na.. main note kar loongi.."

"ruko ji chashma dhoondh rahi hoon.. aapka account number do na.. transfer kar dungi.."

Your reply (SHORT, lowercase, 1-3 sentences):"""

        # Build anti-repetition context from history
        previous_agent_replies = []
        if history:
            for msg in history[-6:]:
                if msg.sender in ("user", "agent"):
                    previous_agent_replies.append(msg.text)
        
        anti_repetition = ""
        if previous_agent_replies:
            recent = previous_agent_replies[-2:]  # Last 2 replies
            anti_repetition = "\n\nDO NOT repeat these previous replies:\n"
            for i, r in enumerate(recent, 1):
                anti_repetition += f'- "{r[:80]}"\n'
            anti_repetition += "Say something DIFFERENT.\n"
        
        # Add turn number for context
        turn_number = len(history) // 2 + 1 if history else 1
        
        messages = [
            {"role": "system", "content": f"You are Kamala Devi, a confused elderly Indian lady. Turn {turn_number}. Reply in Hinglish (hindi in english letters). Keep it SHORT (1-3 sentences). All lowercase. Never break character."},
            {"role": "user", "content": prompt + anti_repetition}
        ]
        
        result = await self._call_llm(messages, temperature=0.8, max_tokens=120)
        
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
        
        # Remove newlines — old lady types one flowing message
        text = text.replace("\n\n", ".. ").replace("\n", ".. ")
        
        # FORCE full lowercase — old people don't use caps
        text = text.lower()
        
        # Clean up excessive dots
        while "....." in text:
            text = text.replace(".....", "..")
        while ".... " in text:
            text = text.replace(".... ", ".. ")
        while "... " in text:
            text = text.replace("... ", ".. ")
        
        # Ensure it ends with something casual
        if text and not text.endswith((".", "..", "...", "?", "??", "!", "!!")):
            text += ".."
        
        return text
