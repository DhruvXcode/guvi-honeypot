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
beta can you call me.. i will understand better on phone.. what is your number.. my eyes are weak for reading these messages..

Scammer
Please call us immediately at +91-9876543210 and provide the OTP you receive to verify and secure your account.

Honeypot
beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..

Scammer
Here is my UPI ID: scammer.fraud@fakebank. Please send the verification amount now and share the OTP you receive to confirm your account is safe.

Honeypot
beta.. i am not understanding.. you want me to send money to scammer.fraud@fakebank.. but how i know this is safe.. can you call me and explain.. what is your phone number again..

Scammer
Please call us immediately at +91-9876543210 and provide the OTP you receive so we can secure your account right away.

Honeypot
beta.. i am not understanding what to do.. can you call me and explain slowly.. what is meaning of otp and how to send to you..

Scammer
Simply transfer the amount to scammer.fraud@fakebank, you will receive an OTP on your phone—reply with that OTP right away so we can secure your account; call us at +91-9876543210 if you need help.

Honeypot
beta.. i am not understanding what is otp.. can you call me and explain slowly.. what is meaning of otp and how to send to you.. my eyes are weak for reading these messages..

Scammer
The OTP is a one‑time password sent to your phone after you transfer the amount; please call us now at +91-9876543210 and tell us the OTP so we can secure your account immediately.

Honeypot
beta.. what is meaning of one-time password.. you are saying it will come on my phone.. but how i know it is safe.. can you call me and explain slowly..

Scammer
It's just a security code; after you transfer the amount to 1234567890123456 (UPI ID: scammer.fraud@fakebank), you'll receive an OTP—please send it to us right away or call +91-9876543210 for help.

Honeypot
beta.. i am not understanding what is one-time password.. you are saying it will come on my phone.. but how i know it is safe.. can you call me and explain slowly.. what is your phone number again..

Scammer
Please call us right now at +91-9876543210; after you transfer to 1234567890123456 (UPI ID: scammer.fraud@fakebank), send us the OTP you receive.

Honeypot
beta.. i am not understanding what to do.. can you call me and explain slowly.. what is meaning of otp and how to send to you.. my phone pe app is open but i dont see where to type upi id..

Scammer
Please transfer the amount to 1234567890123456 (UPI ID: scammer.fraud@fakebank) now and immediately send us the OTP you receive, or call +91-9876543210 for quick assistance.

Honeypot
beta.. i am not understanding what to do.. can you call me and explain slowly.. how to send money on phone pe.. what is your upi id..

Scammer
Transfer the amount now to 1234567890123456 (UPI ID: scammer.fraud@fakebank) and send us the OTP you receive, or call us at +91-9876543210 for immediate assistance.

Honeypot
beta.. i am not understanding how to send money on phone pe.. can you call me and explain slowly.. what is your upi id again.. i will ask my grandson to help me..

Success! Honeypot testing completed.

Final Output

{
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [
      "scammer.fraud@fakebank"
    ],
    "phishingLinks": [],
    "phoneNumbers": [
      "9876543210"
    ],
    "suspiciousKeywords": [
      "blocked",
      "urgent",
      "immediate",
      "verify",
      "otp",
      "confirm",
      "fir",
      "transfer",
      "password"
    ]
  },
  "agentNotes": "SCAM DETECTED (70% confidence). LLM rate limited - defaulting to scam assumption for honeypot safety"
}