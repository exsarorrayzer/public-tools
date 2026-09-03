from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
        self._file_write_enabled = True
        self._ensure_log_directory()
        
        self.uhq_file = self.log_file_path.parent / "uhq.txt"
        self.hq_file = self.log_file_path.parent / "hq.txt"
        self.bad_file = self.log_file_path.parent / "bad.txt"
        
    def _ensure_log_directory(self):
        try:
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            self._file_write_enabled = False
            self._console_output(f"[ERROR] Failed to create log directory: {e}")
    
    def _format_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _console_output(self, message: str):
        print(message)
    
    def _file_output(self, message: str):
        if not self._file_write_enabled:
            return
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except (OSError, PermissionError, IOError) as e:
            self._file_write_enabled = False
            self._console_output(f"[ERROR] Failed to write to log file: {e}")
    
    def _log(self, message: str):
        self._console_output(message)
        self._file_output(message)
    
    def log_generated(self, url: str):
        timestamp = self._format_timestamp()
        message = f"[{timestamp}] [GENERATED] {url}"
        self._log(message)
    
    def log_validation(self, url: str, exists: bool):
        timestamp = self._format_timestamp()
        status = "EXISTS" if exists else "NOT_EXISTS"
        message = f"[{timestamp}] [VALIDATION] {url} - {status}"
        self._log(message)
    
    def log_redirect(self, source: str, destination: str):
        timestamp = self._format_timestamp()
        message = f"[{timestamp}] [REDIRECT] {source} -> {destination}"
        self._log(message)
    
    def log_classification(self, url: str, tier: str):
        timestamp = self._format_timestamp()
        message = f"[{timestamp}] [CLASSIFICATION] {url} - {tier}"
        self._log(message)
        
        self._write_to_tier_file(url, tier)
    
    def _write_to_tier_file(self, url: str, tier: str):
        if not self._file_write_enabled:
            return
        
        try:
            if tier == "UHQ":
                target_file = self.uhq_file
            elif tier == "HQ":
                target_file = self.hq_file
            elif tier == "BAD":
                target_file = self.bad_file
            else:
                return
            
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
        except (OSError, PermissionError, IOError):
            pass
    
    def log_error(self, message: str):
        timestamp = self._format_timestamp()
        log_message = f"[{timestamp}] [ERROR] {message}"
        self._log(log_message)
