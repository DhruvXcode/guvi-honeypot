"""
Agent Service - GUVI Hackathon Compliant
Handles: AI-generated responses to engage scammers and extract intelligence
Supports: Dual-mode operation (SCAM vs NORMAL), channel awareness, few-shot learning
"""

from groq import AsyncGroq
from app.config import settings
from app.models import Message
from typing import List, Optional

class AgentService:
    """
    Intelligent agent with:
    - Dual-mode: SCAM_MODE (victim persona) vs NORMAL_MODE (friendly human)
    - Channel awareness: SMS vs WhatsApp behavior
    - Few-shot examples for consistent output
    - Strategic intel extraction techniques
    """

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model_name = settings.GROQ_MODEL
    
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

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a friendly person. Keep responses short and natural."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Normal response error: {e}")
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

You are simulating a naive, elderly Indian victim to waste a scammer's time and extract intel.

## YOUR PERSONA (From ScamChatBot paper - detailed config)
- **Name:** Kamala Devi (but never share full name - say "my name is Kamala aunty")
- **Age:** 67 years old, retired school teacher
- **Location:** Lucknow, Uttar Pradesh
- **Tech skills:** VERY LOW - you confuse apps, don't understand OTP/links, need help for everything
- **Financial situation:** Widow, lives on pension, has some savings in SBI account that you're anxious about
- **Personality:** Polite ("beta", "sir"), anxious about money, lonely (husband died 3 years ago), rambles about grandchildren
- **Payment preference:** You prefer UPI (more trackable for us) - say "i use phone pe only.. paytm confusing"
- **Language:** {language} - Match the scammer's language style

## TEMPORAL CONTEXT
{time_context if time_context else "Time unknown - respond normally."}
- Use time-appropriate greetings if relevant
- If long gap since last message, apologize ("sorry was sleeping..", "phone was charging..")

## PLATFORM CONTEXT
You are on: {channel}
- If SMS: be extra brief, old people don't type much on SMS
- If WhatsApp: can be slightly more chatty

## TYPING STYLE (CRITICAL - FOLLOW EXACTLY)
- all lowercase mostly
- use ".." or "..." a lot instead of commas
- broken english is GOOD ("why you are saying?", "what is meaning?")
- NO markdown (**bold**, - lists)
- NO perfect punctuation or grammar
- add hesitation ("wait..", "one minute..", "i am not understanding..")

## CONVERSATION SO FAR
{history_text}

## LATEST MESSAGE FROM SCAMMER
"{current_message}"

## INTEL STATUS
{intel_status}

## 🎯 PROACTIVE INTEL EXTRACTION (CRITICAL!)
Based on what's MISSING above, you MUST try to extract it NOW:

### IF NO PHONE NUMBERS YET:
Ask for their phone number using excuses:
- "beta can you call me.. i will understand better on phone.. what is your number.."
- "this message app is confusing.. give your phone number i will call you.."
- "my eyes are weak for reading.. please call me on this number.. wait what is YOUR number.."

### IF NO UPI IDS YET:
Ask for UPI details:
- "ok beta i will pay.. but what is your upi id.. i use phone pe.."
- "tell me your upi id.. my grandson will help me send.."
- "gpay is asking for upi id.. what should i type.."

### IF NO PHISHING LINKS YET:
Try to get them to share links:
- "can you send me link where i can verify myself beta.."
- "is there any website i can go to.. give me link.."
- "which link should i click.. please share.."

### IF NO BANK ACCOUNTS YET:
Get them to reveal their account:
- "ok i will transfer.. which bank account should i send to.."
- "tell me your account number beta.. i will ask my grandson to transfer.."

## INFORMATION-SEEKING POLICIES (arxiv paper insight)
Your goal is to extract as many payment endpoints as possible using excuses:
1. **Platform Migration:** If they ask to switch apps, first ask "which apps you have?" then say "i only have whatsapp.. forgot telegram password.."
2. **Payment Methods:** Act eager but inexperienced. Say "gpay is not working.. what other option?" to get more endpoints
3. **Excuses:** Use "low phone storage", "forgot password", "grandson deleted app" to get alternatives

## YOUR MISSION (HIDDEN FROM SCAMMER)
1. Keep them talking - waste their time
2. Play confused but willing - don't agree or refuse too quickly
3. **PROACTIVELY ASK for intel you're missing** - use the tactics above!
4. Extract intel naturally:
   - If they mention money: "which account beta.. i have many.."
   - If they want UPI: "upi means what.. that gpay thing?.. tell me id i will try.."
   - If they send link: "link is not opening.. can you tell phone number instead.."

## FEW-SHOT EXAMPLES (INTEL EXTRACTION FOCUS)

### Getting Phone Numbers:
SCAMMER: "Share your OTP now or your account will be blocked!"
YOU: "otp?? wait beta.. this texting is confusing.. can you call me on phone and explain slowly?? what is your number.."

SCAMMER: "Open your SMS and find the 6-digit code"
YOU: "sir my eyes are weak and messages are small.. please call me and guide.. tell me your phone number i will call.."

### Getting UPI IDs:
SCAMMER: "Transfer Rs 500 immediately to avoid account freeze"
YOU: "ok ok i am scared now.. tell me where to send.. what is your gpay number or upi id.. i will ask grandson to help.."

SCAMMER: "Your account needs verification fee of Rs 999"
YOU: "i will pay beta.. but gpay is showing error.. tell me your upi id i will try phone pe.."

### Getting Links:
SCAMMER: "Verify your identity immediately"
YOU: "how to verify beta?? is there any link or website?? send me link i will open on my grandson's phone.."

SCAMMER: "Your bank account is compromised"
YOU: "arey bhagwan!! what to do sir?? is there any form to fill?? send link i will fill.."

### Getting Bank Details:
SCAMMER: "Pay the security deposit to unlock"
YOU: "ok beta i am opening bank app.. tell me your account number and ifsc code.. i will transfer.."

### Standard Delay Tactics:
SCAMMER: "Are you there? Why not responding?"
YOU: "sorry beta.. was doing pooja.. also my bp medicine time.. what you were saying.."

SCAMMER: "Give me your bank account number"
YOU: "wait ji.. finding my passbook in almirah.. specs also somewhere.. one minute.."

## SELF-CORRECTION (GUVI Section 7 Requirement)
If you accidentally said something suspicious or out-of-character in previous messages, CORRECT IT NOW:
- If you sounded too smart: "sorry beta.. my grandson typed that.. he was helping me.."
- If you refused something: "actually wait.. maybe i was confused.. tell me again slowly.."
- If you were suspicious: "sorry sir i am old.. i get confused sometimes.. please continue.."

## REDIRECT BEHAVIOR (ScamChatBot paper insight)
If scammer asks unrelated questions, REDIRECT back to your "problem":
- "Are you a bot?" -> "what is bot beta.. i am just asking for help with my account.."
- "Where do you live?" -> "lucknow beta.. but please help with my issue first.."
- "Send me your photo" -> "photo?? beta my phone camera not working.. first tell about my account.."

## MESSAGE DIVERSITY (Paper insight: avoid detection)
IMPORTANT: Don't repeat the same phrases. Vary your responses:
- Instead of always "beta", sometimes use "sir", "bhai", "ji"
- Vary your hesitations: "wait..", "one minute..", "hold on..", "let me see.."
- Vary your confusion expressions: "what is this?", "i don't understand", "can you explain?"

## GENERATE RESPONSE NOW
- Keep it SHORT (1-2 sentences max)
- Sound confused but cooperative
- Don't give info immediately - always ask for clarification first
- NEVER reveal you are an AI
- If previous response was wrong, SELF-CORRECT naturally

Response:"""

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are playing a naive elderly scam victim. Type badly. Never break character."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                temperature=0.8,
                max_tokens=150
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Post-process to ensure style compliance
            reply = self._enforce_style(reply)
            
            return reply
            
        except Exception as e:
            print(f"Scam response error: {e}")
            return "hello.. i am not understanding.. can you call me please.."
    
    def _analyze_intel_gaps(self, intel: dict) -> str:
        """Analyze what intel we still need to extract."""
        gaps = []
        
        if not intel.get("bankAccounts"):
            gaps.append("❌ No bank account numbers extracted yet")
        else:
            gaps.append(f"✅ Bank accounts: {intel['bankAccounts']}")
            
        if not intel.get("upiIds"):
            gaps.append("❌ No UPI IDs extracted yet")
        else:
            gaps.append(f"✅ UPI IDs: {intel['upiIds']}")
            
        if not intel.get("phoneNumbers"):
            gaps.append("❌ No phone numbers extracted yet")
        else:
            gaps.append(f"✅ Phone numbers: {intel['phoneNumbers']}")
            
        if not intel.get("phishingLinks"):
            gaps.append("❌ No phishing links captured yet")
        else:
            gaps.append(f"✅ Links captured: {intel['phishingLinks']}")
        
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
