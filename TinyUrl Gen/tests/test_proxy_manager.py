import pytest
from src.proxy_manager import ProxyManager
from src.models import ProxyConfig


class TestProxyManagerInitialization:
    def test_init_with_none_config(self):
        manager = ProxyManager(None)
        assert manager.config is None
    
    def test_init_with_valid_config(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="http")
        manager = ProxyManager(config)
        assert manager.config == config


class TestProxyManagerValidation:
    def test_invalid_host_empty_string(self):
        config = ProxyConfig(host="", port=8080, protocol="http")
        with pytest.raises(ValueError, match="Host must be a non-empty string"):
            ProxyManager(config)
    
    def test_invalid_host_non_string(self):
        config = ProxyConfig(host=None, port=8080, protocol="http")
        with pytest.raises(ValueError, match="Host must be a non-empty string"):
            ProxyManager(config)
    
    def test_invalid_host_format(self):
        config = ProxyConfig(host="invalid_host!", port=8080, protocol="http")
        with pytest.raises(ValueError, match="Invalid host format"):
            ProxyManager(config)
    
    def test_valid_host_hostname(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="http")
        manager = ProxyManager(config)
        assert manager.config.host == "proxy.example.com"
    
    def test_valid_host_ipv4(self):
        config = ProxyConfig(host="192.168.1.1", port=8080, protocol="http")
        manager = ProxyManager(config)
        assert manager.config.host == "192.168.1.1"
    
    def test_invalid_port_zero(self):
        config = ProxyConfig(host="proxy.example.com", port=0, protocol="http")
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            ProxyManager(config)
    
    def test_invalid_port_negative(self):
        config = ProxyConfig(host="proxy.example.com", port=-1, protocol="http")
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            ProxyManager(config)
    
    def test_invalid_port_too_high(self):
        config = ProxyConfig(host="proxy.example.com", port=65536, protocol="http")
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            ProxyManager(config)
    
    def test_valid_port_boundary_lower(self):
        config = ProxyConfig(host="proxy.example.com", port=1, protocol="http")
        manager = ProxyManager(config)
        assert manager.config.port == 1
    
    def test_valid_port_boundary_upper(self):
        config = ProxyConfig(host="proxy.example.com", port=65535, protocol="http")
        manager = ProxyManager(config)
        assert manager.config.port == 65535
    
    def test_invalid_protocol_ftp(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="ftp")
        with pytest.raises(ValueError, match="Protocol must be 'http' or 'https'"):
            ProxyManager(config)
    
    def test_invalid_protocol_empty(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="")
        with pytest.raises(ValueError, match="Protocol must be 'http' or 'https'"):
            ProxyManager(config)
    
    def test_valid_protocol_http(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="http")
        manager = ProxyManager(config)
        assert manager.config.protocol == "http"
    
    def test_valid_protocol_https(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="https")
        manager = ProxyManager(config)
        assert manager.config.protocol == "https"


class TestProxyManagerHTTPClient:
    def test_get_http_client_without_proxy(self):
        manager = ProxyManager(None)
        session = manager.get_http_client()
        assert session is not None
        assert session.proxies == {}
    
    def test_get_http_client_with_http_proxy(self):
        config = ProxyConfig(host="proxy.example.com", port=8080, protocol="http")
        manager = ProxyManager(config)
        session = manager.get_http_client()
        assert session is not None
        assert session.proxies["http"] == "http://proxy.example.com:8080"
        assert session.proxies["https"] == "http://proxy.example.com:8080"
    
    def test_get_http_client_with_https_proxy(self):
        config = ProxyConfig(host="proxy.example.com", port=8443, protocol="https")
        manager = ProxyManager(config)
        session = manager.get_http_client()
        assert session is not None
        assert session.proxies["http"] == "https://proxy.example.com:8443"
        assert session.proxies["https"] == "https://proxy.example.com:8443"
    
    def test_get_http_client_with_ip_proxy(self):
        config = ProxyConfig(host="10.0.0.1", port=3128, protocol="http")
        manager = ProxyManager(config)
        session = manager.get_http_client()
        assert session is not None
        assert session.proxies["http"] == "http://10.0.0.1:3128"
        assert session.proxies["https"] == "http://10.0.0.1:3128"
    
    def test_get_http_client_returns_new_session(self):
        manager = ProxyManager(None)
        session1 = manager.get_http_client()
        session2 = manager.get_http_client()
        assert session1 is not session2
