from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from src.proxy_manager import ProxyManager
from src.logger import Logger


class LinkChecker:
    MAX_REDIRECT_DEPTH = 10
    REQUEST_TIMEOUT = 10
    
    def __init__(self, proxy_manager: ProxyManager, logger: Logger):
        self.proxy_manager = proxy_manager
        self.logger = logger
        self._session = None
    
    def _get_session(self) -> requests.Session:
        if self._session is None:
            self._session = self.proxy_manager.get_http_client()
        return self._session
    
    def check_existence(self, url: str) -> bool:
        try:
            session = self._get_session()
            response = session.head(url, allow_redirects=False, timeout=self.REQUEST_TIMEOUT)
            exists = response.status_code < 400
            self.logger.log_validation(url, exists)
            return exists
        except (Timeout, ConnectionError) as e:
            self.logger.log_validation(url, False)
            return False
        except RequestException as e:
            self.logger.log_error(f"Connection error checking {url}: {e}")
            self.logger.log_validation(url, False)
            return False
    
    def get_redirect_destination(self, url: str) -> Optional[str]:
        if not self.check_existence(url):
            return None
        
        try:
            session = self._get_session()
            session.max_redirects = self.MAX_REDIRECT_DEPTH
            response = session.get(url, allow_redirects=True, timeout=self.REQUEST_TIMEOUT)
            
            destination = response.url
            self.logger.log_redirect(url, destination)
            return destination
        except requests.TooManyRedirects:
            self.logger.log_error(f"Too many redirects for {url} (exceeded {self.MAX_REDIRECT_DEPTH} hops)")
            return None
        except (Timeout, ConnectionError) as e:
            self.logger.log_error(f"Connection error retrieving redirect for {url}: {e}")
            return None
        except RequestException as e:
            self.logger.log_error(f"Error retrieving redirect for {url}: {e}")
            return None
