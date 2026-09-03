import re
import random
import warnings
from typing import Optional, List
from pathlib import Path
import requests
from src.models import ProxyConfig

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class ProxyManager:
    TEST_URL = "http://ip-api.com/json/"
    TEST_TIMEOUT = 5
    
    def __init__(self, config: Optional[ProxyConfig] = None, proxy_file: Optional[str] = None, test_proxies: bool = True):
        self.config = config
        self.proxy_file = proxy_file
        self.proxy_list: List[ProxyConfig] = []
        self.test_proxies = test_proxies
        
        if proxy_file:
            self._load_proxy_file(proxy_file)
            if test_proxies and self.proxy_list:
                self._test_all_proxies()
        elif config:
            self._validate_config(config)
    
    def _validate_config(self, config: ProxyConfig):
        self._validate_host(config.host)
        self._validate_port(config.port)
        self._validate_protocol(config.protocol)
    
    def _validate_host(self, host: str):
        if not host or not isinstance(host, str):
            raise ValueError("Host must be a non-empty string")
        
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        if not (re.match(hostname_pattern, host) or re.match(ipv4_pattern, host)):
            raise ValueError(f"Invalid host format: {host}")
    
    def _validate_port(self, port: int):
        if not isinstance(port, int):
            raise ValueError("Port must be an integer")
        
        if port < 1 or port > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {port}")
    
    def _validate_protocol(self, protocol: str):
        if protocol not in {"http", "https"}:
            raise ValueError(f"Protocol must be 'http' or 'https', got '{protocol}'")
    
    def _load_proxy_file(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Proxy file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        for line in lines:
            try:
                proxy_config = self._parse_proxy_line(line)
                self._validate_config(proxy_config)
                self.proxy_list.append(proxy_config)
            except ValueError as e:
                continue
        
        if not self.proxy_list:
            raise ValueError(f"No valid proxies found in {file_path}")
    
    def _parse_proxy_line(self, line: str) -> ProxyConfig:
        line = line.strip()
        
        username = None
        password = None
        
        if line.startswith('http://') or line.startswith('https://'):
            protocol = 'https' if line.startswith('https://') else 'http'
            line = line.replace('http://', '').replace('https://', '')
        else:
            protocol = 'http'
        
        if '@' in line:
            auth_part, server_part = line.split('@', 1)
            if ':' in auth_part:
                username, password = auth_part.split(':', 1)
            line = server_part
        
        if ':' not in line:
            raise ValueError(f"Invalid proxy format: {line}")
        
        parts = line.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid proxy format: {line}")
        
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid port in proxy: {line}")
        
        return ProxyConfig(host=host, port=port, protocol=protocol, username=username, password=password)
    
    def _get_random_proxy(self) -> Optional[ProxyConfig]:
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)
    
    def _test_proxy(self, proxy_config: ProxyConfig) -> tuple[bool, Optional[str]]:
        try:
            if proxy_config.username and proxy_config.password:
                proxy_url = f"http://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
            else:
                proxy_url = f"http://{proxy_config.host}:{proxy_config.port}"
            
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            response = requests.get(self.TEST_URL, proxies=proxies, timeout=self.TEST_TIMEOUT, verify=False)
            if response.status_code == 200:
                data = response.json()
                country = data.get("country", "Unknown")
                return True, country
            return False, None
        except Exception as e:
            return False, None
    
    def _test_all_proxies(self):
        if not self.proxy_list:
            return
        
        working_proxies = []
        total = len(self.proxy_list)
        
        print(f"\n[Testing {total} proxies...]\n")
        
        for idx, proxy in enumerate(self.proxy_list, 1):
            working, country = self._test_proxy(proxy)
            if working:
                working_proxies.append(proxy)
                print(f"[OK] [{idx}/{total}] {proxy.host}:{proxy.port} - {country}")
            else:
                print(f"[FAIL] [{idx}/{total}] {proxy.host}:{proxy.port}")
        
        self.proxy_list = working_proxies
        print(f"\n[{len(working_proxies)}/{total} proxies working]\n")
    
    def get_http_client(self) -> requests.Session:
        session = requests.Session()
        
        proxy_config = None
        if self.proxy_list:
            proxy_config = self._get_random_proxy()
        elif self.config:
            proxy_config = self.config
        
        if proxy_config:
            if proxy_config.username and proxy_config.password:
                proxy_url = f"{proxy_config.protocol}://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
            else:
                proxy_url = f"{proxy_config.protocol}://{proxy_config.host}:{proxy_config.port}"
            
            session.proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
        
        return session
