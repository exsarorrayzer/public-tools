import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import requests
from src.link_checker import LinkChecker
from src.proxy_manager import ProxyManager
from src.logger import Logger
from src.models import ProxyConfig


class TestLinkCheckerInitialization:
    def test_init_with_proxy_manager_and_logger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            assert checker.proxy_manager == proxy_manager
            assert checker.logger == logger


class TestLinkCheckerExistence:
    def test_existing_url_returns_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_response
                mock_client.return_value = mock_session
                
                result = checker.check_existence("https://example.com/test")
                assert result is True
    
    def test_non_existing_url_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_response = Mock()
            mock_response.status_code = 404
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_response
                mock_client.return_value = mock_session
                
                result = checker.check_existence("https://example.com/notfound")
                assert result is False
    
    def test_redirect_status_returns_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_response = Mock()
            mock_response.status_code = 301
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_response
                mock_client.return_value = mock_session
                
                result = checker.check_existence("https://example.com/redirect")
                assert result is True
    
    def test_timeout_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.side_effect = requests.exceptions.Timeout()
                mock_client.return_value = mock_session
                
                result = checker.check_existence("https://example.com/timeout")
                assert result is False
    
    def test_connection_error_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.side_effect = requests.exceptions.ConnectionError()
                mock_client.return_value = mock_session
                
                result = checker.check_existence("https://example.com/error")
                assert result is False


class TestLinkCheckerRedirect:
    def test_non_existing_url_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_response = Mock()
            mock_response.status_code = 404
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_response
                mock_client.return_value = mock_session
                
                result = checker.get_redirect_destination("https://example.com/notfound")
                assert result is None
    
    def test_existing_url_returns_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_head_response = Mock()
            mock_head_response.status_code = 301
            
            mock_get_response = Mock()
            mock_get_response.url = "https://final-destination.com/page"
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_head_response
                mock_session.get.return_value = mock_get_response
                mock_client.return_value = mock_session
                
                result = checker.get_redirect_destination("https://example.com/redirect")
                assert result == "https://final-destination.com/page"
    
    def test_too_many_redirects_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_head_response = Mock()
            mock_head_response.status_code = 301
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_head_response
                mock_session.get.side_effect = requests.exceptions.TooManyRedirects()
                mock_client.return_value = mock_session
                
                result = checker.get_redirect_destination("https://example.com/loop")
                assert result is None
    
    def test_redirect_timeout_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_head_response = Mock()
            mock_head_response.status_code = 301
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_head_response
                mock_session.get.side_effect = requests.exceptions.Timeout()
                mock_client.return_value = mock_session
                
                result = checker.get_redirect_destination("https://example.com/slow")
                assert result is None


class TestLinkCheckerLogging:
    def test_logs_validation_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_response
                mock_client.return_value = mock_session
                
                checker.check_existence("https://example.com/test")
                
                log_content = log_path.read_text()
                assert "VALIDATION" in log_content
                assert "https://example.com/test" in log_content
                assert "EXISTS" in log_content
    
    def test_logs_redirect_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            mock_head_response = Mock()
            mock_head_response.status_code = 301
            
            mock_get_response = Mock()
            mock_get_response.url = "https://final.com/page"
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.return_value = mock_head_response
                mock_session.get.return_value = mock_get_response
                mock_client.return_value = mock_session
                
                checker.get_redirect_destination("https://example.com/redirect")
                
                log_content = log_path.read_text()
                assert "REDIRECT" in log_content
                assert "https://example.com/redirect" in log_content
                assert "https://final.com/page" in log_content
    
    def test_logs_error_on_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            proxy_manager = ProxyManager(None)
            checker = LinkChecker(proxy_manager, logger)
            
            with patch.object(checker.proxy_manager, 'get_http_client') as mock_client:
                mock_session = Mock()
                mock_session.head.side_effect = requests.exceptions.RequestException("Connection failed")
                mock_client.return_value = mock_session
                
                checker.check_existence("https://example.com/error")
                
                log_content = log_path.read_text()
                assert "ERROR" in log_content
