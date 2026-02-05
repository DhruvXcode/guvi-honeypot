"""
Intelligence Extraction Service - GUVI Hackathon Compliant
Handles: Extracting bank accounts, UPI IDs, phone numbers, URLs, and keywords from messages
"""

import re
from typing import List, Set
from ..models import ExtractedIntelligence


class IntelligenceService:
    """
    Service to extract intelligence from scammer messages.
    
    Extracts:
    - Bank account numbers (9-18 digits with context)
    - UPI IDs (user@bank format, excludes emails)
    - Phone numbers (Indian format +91/10 digits)
    - URLs (potential phishing links)
    - Suspicious keywords
    """

    def __init__(self):
        # ============== BANK ACCOUNT PATTERNS ==============
        # Look for account numbers with context (a/c, account, no, number)
        self.bank_account_patterns = [
            r"(?i)(?:a/c|acct|account|acc)[.\s:-]*(?:no|number)?[.\s:-]*(\d{9,18})",
            r"(?i)(?:account|a/c)\s*(\d{9,18})",
            # Standalone 11-16 digit numbers (common account/card number formats)
            # Excluding 10-digit phone numbers and 13-digit timestamps
            r"\b(\d{11,16})\b",
        ]
        
        # ============== UPI PATTERNS ==============
        # UPI format: username@bankhandle
        self.upi_pattern = r"([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)"
        
        # Email domains to exclude (not UPI handles)
        self.email_domains = {
            "gmail", "yahoo", "hotmail", "outlook", "rediffmail", 
            "protonmail", "icloud", "mail", "email", "live", "msn"
        }
        
        # Known UPI handles (positive match)
        self.upi_handles = {
            "upi", "paytm", "okhdfcbank", "okicici", "oksbi", "ybl",
            "apl", "axl", "ibl", "sbi", "hdfc", "icici", "axis",
            "kotak", "indus", "federal", "gpay", "phonepe", "amazonpay",
            "freecharge", "airtel", "jio", "mobikwik", "slice", "cred",
            "idfcfirst", "rbl", "dbs", "yes", "bob", "pnb", "canara"
        }
        
        # ============== URL PATTERNS ==============
        self.url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
        
        # ============== PHONE PATTERNS ==============
        # Indian phone: +91XXXXXXXXXX or 10 digits starting with 6-9
        self.phone_patterns = [
            r"\+91[\s.-]?(\d{5})[\s.-]?(\d{5})",  # +91 12345 67890
            r"\+91[\s.-]?(\d{10})",  # +91 1234567890
            r"\b([6-9]\d{9})\b",  # 9876543210
        ]
        
        # ============== SUSPICIOUS KEYWORDS ==============
        self.suspicious_keywords = [
            # Urgency
            "blocked", "suspend", "expired", "urgent", "immediate", "today",
            # Verification
            "verify", "kyc", "update", "confirm", "validate",
            # Credentials
            "otp", "pin", "password", "cvv", "card number",
            # Money
            "refund", "prize", "lottery", "winner", "cashback", "reward",
            # Threats
            "legal action", "police", "arrest", "court", "fir",
            # Technical
            "download", "apk", "install", "click here", "link",
            # Finance
            "pan card", "aadhar", "aadhaar", "bank account", "transfer"
        ]

    def extract(self, text: str) -> ExtractedIntelligence:
        """Extract all intelligence from a single message text."""
        intel = ExtractedIntelligence()
        
        if not text:
            return intel
        
        text_lower = text.lower()
        
        # ============== EXTRACT BANK ACCOUNTS ==============
        for pattern in self.bank_account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Flatten tuple if needed
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[-1]
                
                # Validate: must be 9-18 digits
                if match.isdigit() and 9 <= len(match) <= 18:
                    # Filter out obvious non-accounts
                    # - Phone numbers (10 digits starting with 6-9)
                    if len(match) == 10 and match[0] in "6789":
                        continue
                    # - Timestamps (10 digits starting with 16/17/18 - unix time)
                    if len(match) == 10 and match.startswith(("16", "17", "18")):
                        continue
                    
                    if match not in intel.bankAccounts:
                        intel.bankAccounts.append(match)
        
        # ============== EXTRACT UPI IDS ==============
        upi_matches = re.findall(self.upi_pattern, text, re.IGNORECASE)
        for match in upi_matches:
            if "@" in match:
                handle = match.split("@")[1].lower()
                
                # Exclude if it's an email domain
                if handle in self.email_domains:
                    continue
                
                # Exclude if handle contains a dot (like .com, .in)
                if "." in handle:
                    continue
                
                # Include if it's a known UPI handle OR doesn't look like email
                if handle in self.upi_handles or len(handle) <= 10:
                    if match.lower() not in [u.lower() for u in intel.upiIds]:
                        intel.upiIds.append(match)
        
        # ============== EXTRACT URLS ==============
        url_matches = re.findall(self.url_pattern, text)
        for url in url_matches:
            # Clean trailing punctuation
            url = url.rstrip(".,;:!?)")
            if url not in intel.phishingLinks:
                intel.phishingLinks.append(url)
        
        # ============== EXTRACT PHONE NUMBERS ==============
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Flatten and clean
                if isinstance(match, tuple):
                    number = "".join(match)
                else:
                    number = match
                
                number = number.replace(" ", "").replace("-", "").replace(".", "")
                
                # Ensure it's 10 digits
                if len(number) == 10 and number.isdigit():
                    if number not in intel.phoneNumbers:
                        intel.phoneNumbers.append(number)
        
        # ============== EXTRACT KEYWORDS ==============
        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                if keyword not in intel.suspiciousKeywords:
                    intel.suspiciousKeywords.append(keyword)
        
        return intel

    def merge_intelligence(
        self, 
        current: ExtractedIntelligence, 
        new_intel: ExtractedIntelligence
    ) -> ExtractedIntelligence:
        """Merge new intelligence into existing collection without duplicates."""
        
        def merge_unique(list1: List[str], list2: List[str]) -> List[str]:
            """Merge two lists, preserving order and removing duplicates."""
            seen = set()
            result = []
            for item in list1 + list2:
                item_lower = item.lower() if isinstance(item, str) else item
                if item_lower not in seen:
                    seen.add(item_lower)
                    result.append(item)
            return result
        
        current.bankAccounts = merge_unique(current.bankAccounts, new_intel.bankAccounts)
        current.upiIds = merge_unique(current.upiIds, new_intel.upiIds)
        current.phishingLinks = merge_unique(current.phishingLinks, new_intel.phishingLinks)
        current.phoneNumbers = merge_unique(current.phoneNumbers, new_intel.phoneNumbers)
        current.suspiciousKeywords = merge_unique(current.suspiciousKeywords, new_intel.suspiciousKeywords)
        
        return current
