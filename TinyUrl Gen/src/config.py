import json
from pathlib import Path
from typing import Optional


class Config:
    DEFAULT_CONFIG = {
        "pattern": r"https://tinyurl\.com/[a-z0-9]{7}",
        "count": 10,
        "log_file": "logs/tinyurl.log",
        "proxy_file": "proxies.txt",
        "test_proxies": True
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.data = self._load()
    
    def _load(self) -> dict:
        if not self.config_path.exists():
            self._save(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()
    
    def _save(self, data: dict):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        self._save(self.data)
    
    def reload(self):
        self.data = self._load()
    
    @property
    def pattern(self) -> str:
        return self.get("pattern", self.DEFAULT_CONFIG["pattern"])
    
    @pattern.setter
    def pattern(self, value: str):
        self.set("pattern", value)
    
    @property
    def count(self) -> int:
        return self.get("count", self.DEFAULT_CONFIG["count"])
    
    @count.setter
    def count(self, value: int):
        self.set("count", value)
    
    @property
    def log_file(self) -> str:
        return self.get("log_file", self.DEFAULT_CONFIG["log_file"])
    
    @log_file.setter
    def log_file(self, value: str):
        self.set("log_file", value)
    
    @property
    def proxy_file(self) -> Optional[str]:
        return self.get("proxy_file", self.DEFAULT_CONFIG["proxy_file"])
    
    @proxy_file.setter
    def proxy_file(self, value: Optional[str]):
        self.set("proxy_file", value)
    
    @property
    def test_proxies(self) -> bool:
        return self.get("test_proxies", True)
    
    @test_proxies.setter
    def test_proxies(self, value: bool):
        self.set("test_proxies", value)
