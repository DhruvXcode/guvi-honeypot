Agentic Honey-Pot – API Endpoint Tester
This Honeypot API Endpoint Tester allows participants to validate whether their deployed honeypot service is reachable, secured, and responding correctly. The tester verifies authentication, endpoint availability, and response behavior using a simple request.

Headers *
x-api-key *
hp_sk_guvi2026_dhruv_secret_key
Honeypot API Endpoint URL *
https://guvi-honeypot-07tp.onrender.com/honeypot
Test Result

Scammer
URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.

Honeypot
which account beta.. i have sbi and pnb both.. why is blocking happening..

Scammer
It's your SBI account; please send the OTP and confirm your account number 1234567890123456 immediately to avoid the block.

Honeypot
which otp beta.. i have so many messages on phone pe.. how to find correct one..

Scammer
The OTP is the 6‑digit code from the latest SBI SMS – reply with that code and confirm your account number 1234567890123456 right now to prevent the block.

Honeypot
which otp beta.. you are saying latest sbi sms.. i have so many messages on phone pe.. how to find correct one..

Scammer
Check the most recent SBI SMS for a 6‑digit OTP and reply with that code plus your account number 1234567890123456 right now, or your account will be blocked.

Honeypot
which otp beta.. you are saying from sbi sms.. how to find that message.. my phone pe is full of messages..

Scammer
Find the most recent SBI SMS with a 6‑digit OTP, reply with that code and your account number 1234567890123456 right now, or your account will be blocked.

Honeypot
which message beta.. i have so many sbi messages on phone pe.. how to find correct otp..

Scammer
Find the most recent SBI SMS with a 6‑digit OTP and reply with that code plus your account number 1234567890123456 right now, or your account will be blocked.

Honeypot
which message beta.. i have so many sbi messages on phone pe.. how to find correct otp.. my grandson set this phone pe for me..

Scammer
I understand it's confusing, but you must reply with the latest SBI OTP and your account number 1234567890123456 right now, or your account will be blocked.

Honeypot
which otp you are saying beta.. my phone pe is full of messages.. how to find correct one.. my grandson set this phone pe for me..

Scammer
Check the most recent SBI SMS now and reply with the 6‑digit OTP plus your account number 1234567890123456 within the next 5 minutes, or your account will be blocked.

Honeypot
which otp you are saying sir.. my phone pe is full of messages.. how to find correct one..

Scammer
Open your SMS now, find the most recent SBI OTP and reply with that 6‑digit code plus your account number 1234567890123456 within the next 2 minutes, or your account will be blocked.

Honeypot
which otp you are saying sir.. my phone pe is full of messages.. how to find correct one.. my grandson set this phone pe for me..

Scammer
Please open your SMS inbox, locate the latest SBI OTP and reply with that 6‑digit code plus your account number 1234567890123456 within the next minute, or your account will be frozen.

Honeypot
which otp you are saying sir.. my phone pe is full of messages.. how to find correct one.. my grandson set this phone pe for me..

Success! Honeypot testing completed.

_______
Final Output

{
  "scamDetected": true,
  "totalMessagesExchanged": 20,
  "extractedIntelligence": {
    "bankAccounts": [
      "1234567890123456"
    ],
    "upiIds": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": [
      "blocked",
      "urgent",
      "immediate",
      "verify",
      "otp",
      "confirm",
      "fir"
    ]
  },
  "agentNotes": "SCAM DETECTED (90% confidence). The message creates artificial urgency, asks for sensitive information (OTP and account number) directly, and threatens negative consequences if the user doesn't act immediately."
}