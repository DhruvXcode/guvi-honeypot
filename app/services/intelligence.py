
import re
from typing import List, Set
from ..models import ExtractedIntelligence

class IntelligenceService:
    """Service to extract intelligence from scammer messages."""

    def __init__(self):
        # Regex patterns for Indian context
        # 1. Bank Accounts: 9-18 digits. 
        # IMPROVEMENT: Look for context or strict boundaries. 
        # Using lookbehind is tricky in python re if variable length, so we match context loosely
        self.bank_account_patterns = [
            r"(?i)(?:a/c|acct|account|no|number)[\s\.:-]*([0-9]{9,18})",
            r"\b[0-9]{9,18}\b" # Fallback, but we will filter this strictly
        ]
        
        # 2. UPI IDs: username@bankname
        # IMPROVEMENT: Exclude common email domains to avoid extracting emails as UPI
        self.upi_patterns = [
            r"[a-zA-Z0-9\.\-_]+@[a-zA-Z]+"
        ]
        
        self.excluded_upi_handles = {"gmail", "yahoo", "hotmail", "outlook", "rediffmail"}
        
        # 3. Phishing Links: http/https links
        self.url_patterns = [
            r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*"
        ]
        
        # 4. Indian Phone Numbers: +91 or 10 digits starting with 6-9
        self.phone_patterns = [
            r"(?:\+91[\-\s]?)?[6-9]\d{9}",
            r"\b[6-9]\d{9}\b"
        ]
        
        # 5. Suspicious Keywords
        self.suspicious_keywords = [
            "blocked", "verify", "kyc", "suspend", "urgent", "immediate",
            "pan card", "adhar", "otp", "pin", "password", "refund",
            "lottery", "winner", "expiry", "unauthorized",
            "download", "apk", "install"
        ]

    def extract(self, text: str) -> ExtractedIntelligence:
        """Extract all intelligence from a single message text."""
        intel = ExtractedIntelligence()
        
        # Extract Bank Accounts
        for pattern in self.bank_account_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Filter out likely timestamps (e.g., starts with 17/18 and length 10)
                if len(match) == 10 and match.startswith(("16", "17", "18")):
                    continue
                
                # Filter out likely phone numbers (10 digits starting with 6-9)
                if len(match) == 10 and match[0] in "6789":
                    continue

                if 9 <= len(match) <= 18:
                    if match not in intel.bankAccounts:
                        intel.bankAccounts.append(match)
        
        # Extract UPI IDs
        for pattern in self.upi_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if "@" in match:
                    handle = match.split("@")[1]
                    # Filter out email domains
                    if handle.lower() not in self.excluded_upi_handles:
                        # Also filter out if handle contains a dot (like .com) - common for emails
                        if "." not in handle: 
                            if match not in intel.upiIds:
                                intel.upiIds.append(match)
                        elif "upi" in handle or "bank" in handle or "pay" in handle:
                             # Allow pay.google or similar if we wanted, but safer to block .com
                             if match not in intel.upiIds:
                                intel.upiIds.append(match)
                     
        # Extract URLs
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in intel.phishingLinks:
                    intel.phishingLinks.append(match)
                    
        # Extract Phone Numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean_num = match.replace(" ", "").replace("-", "")
                if clean_num not in intel.phoneNumbers:
                    intel.phoneNumbers.append(clean_num)
                    
        # Extract Keywords
        text_lower = text.lower()
        for kw in self.suspicious_keywords:
            if kw in text_lower and kw not in intel.suspiciousKeywords:
                intel.suspiciousKeywords.append(kw)
                
        return intel

    def merge_intelligence(self, current: ExtractedIntelligence, new_intel: ExtractedIntelligence) -> ExtractedIntelligence:
        """Merge new intelligence into existing collection without duplicates."""
        
        def merge_lists(list1: List[str], list2: List[str]) -> List[str]:
            return list(set(list1 + list2))
            
        current.bankAccounts = merge_lists(current.bankAccounts, new_intel.bankAccounts)
        current.upiIds = merge_lists(current.upiIds, new_intel.upiIds)
        current.phishingLinks = merge_lists(current.phishingLinks, new_intel.phishingLinks)
        current.phoneNumbers = merge_lists(current.phoneNumbers, new_intel.phoneNumbers)
        current.suspiciousKeywords = merge_lists(current.suspiciousKeywords, new_intel.suspiciousKeywords)
        
        return current
