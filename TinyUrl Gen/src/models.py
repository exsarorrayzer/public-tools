from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ProxyConfig:
    host: str
    port: int
    protocol: str
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class ValidationResult:
    url: str
    exists: bool
    destination: Optional[str]
    quality_tier: Optional[str]
    timestamp: datetime


@dataclass
class GenerationResult:
    candidates: List[str]
    timestamp: datetime
