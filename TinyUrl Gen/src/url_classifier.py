from typing import Optional


class URLClassifier:
    UHQ_DOMAINS = ["mega.nz", "mediafire.com"]
    HQ_DOMAINS = ["justpaste.it", "youtube.com"]
    HQ_COMBINED_KEYWORDS = [("google", "drive")]
    
    def classify(self, url: Optional[str]) -> str:
        if not url:
            return "BAD"
        
        url_lower = url.lower()
        
        for domain in self.UHQ_DOMAINS:
            if domain in url_lower:
                return "UHQ"
        
        for domain in self.HQ_DOMAINS:
            if domain in url_lower:
                return "HQ"
        
        for keywords in self.HQ_COMBINED_KEYWORDS:
            if all(keyword in url_lower for keyword in keywords):
                return "HQ"
        
        return "BAD"
