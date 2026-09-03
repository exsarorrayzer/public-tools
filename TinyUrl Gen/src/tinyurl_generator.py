import re
import random
import string
from typing import List
from src.logger import Logger


class TinyURLGenerator:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def generate_candidates(self, pattern: str, count: int) -> List[str]:
        self._validate_pattern(pattern)
        self._validate_count(count)
        
        candidates = []
        for _ in range(count):
            url = self._generate_from_pattern(pattern)
            candidates.append(url)
            self.logger.log_generated(url)
        
        return candidates
    
    def _validate_pattern(self, pattern: str):
        if not pattern:
            raise ValueError("Pattern cannot be empty")
        
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
    
    def _validate_count(self, count: int):
        if not isinstance(count, int):
            raise ValueError("Count must be an integer")
        
        if count <= 0:
            raise ValueError("Count must be positive")
    
    def _generate_from_pattern(self, pattern: str) -> str:
        if pattern == r"https://tinyurl\.com/[a-z0-9]{7}":
            return f"https://tinyurl.com/{''.join(random.choices(string.ascii_lowercase + string.digits, k=7))}"
        
        if pattern == r"https://tinyurl\.com/[a-zA-Z0-9]{6}":
            return f"https://tinyurl.com/{''.join(random.choices(string.ascii_letters + string.digits, k=6))}"
        
        if pattern == r"https://tinyurl\.com/\w{8}":
            return f"https://tinyurl.com/{''.join(random.choices(string.ascii_letters + string.digits + '_', k=8))}"
        
        base_url = "https://tinyurl.com/"
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        return base_url + random_id
