import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from src.logger import Logger


class TestLoggerInitialization:
    def test_creates_log_directory_if_not_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "subdir" / "logs" / "test.log"
            logger = Logger(str(log_path))
            assert log_path.parent.exists()
    
    def test_handles_existing_log_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            assert log_path.parent.exists()
    
    def test_handles_permission_denied_on_directory_creation(self):
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with patch('builtins.print') as mock_print:
                logger = Logger("/root/forbidden/test.log")
                assert not logger._file_write_enabled
                mock_print.assert_called_once()
                assert "Failed to create log directory" in str(mock_print.call_args)


class TestLogGenerated:
    def test_logs_to_console_and_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            with patch('builtins.print') as mock_print:
                logger.log_generated("https://tinyurl.com/test123")
                mock_print.assert_called_once()
                call_args = str(mock_print.call_args)
                assert "GENERATED" in call_args
                assert "https://tinyurl.com/test123" in call_args
            
            content = log_path.read_text()
            assert "GENERATED" in content
            assert "https://tinyurl.com/test123" in content
    
    def test_includes_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            logger.log_generated("https://tinyurl.com/test123")
            
            content = log_path.read_text()
            assert content.startswith("[20")


class TestLogValidation:
    def test_logs_exists_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_validation("https://tinyurl.com/test123", True)
            content = log_path.read_text()
            assert "VALIDATION" in content
            assert "https://tinyurl.com/test123" in content
            assert "EXISTS" in content
    
    def test_logs_not_exists_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_validation("https://tinyurl.com/test123", False)
            content = log_path.read_text()
            assert "VALIDATION" in content
            assert "https://tinyurl.com/test123" in content
            assert "NOT_EXISTS" in content
    
    def test_includes_timestamp_and_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            logger.log_validation("https://tinyurl.com/abc", True)
            
            content = log_path.read_text()
            assert content.startswith("[20")
            assert "https://tinyurl.com/abc" in content


class TestLogRedirect:
    def test_logs_source_and_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_redirect(
                "https://tinyurl.com/test123",
                "https://mega.nz/file/abc123"
            )
            content = log_path.read_text()
            assert "REDIRECT" in content
            assert "https://tinyurl.com/test123" in content
            assert "https://mega.nz/file/abc123" in content
            assert "->" in content
    
    def test_includes_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            logger.log_redirect("https://tinyurl.com/src", "https://example.com/dest")
            
            content = log_path.read_text()
            assert content.startswith("[20")


class TestLogClassification:
    def test_logs_uhq_classification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_classification("https://mega.nz/file/abc", "UHQ")
            content = log_path.read_text()
            assert "CLASSIFICATION" in content
            assert "https://mega.nz/file/abc" in content
            assert "UHQ" in content
    
    def test_logs_hq_classification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_classification("https://justpaste.io/test", "HQ")
            content = log_path.read_text()
            assert "HQ" in content
    
    def test_logs_bad_classification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_classification("https://example.com/page", "BAD")
            content = log_path.read_text()
            assert "BAD" in content
    
    def test_includes_timestamp_and_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            logger.log_classification("https://test.com", "BAD")
            
            content = log_path.read_text()
            assert content.startswith("[20")
            assert "https://test.com" in content


class TestLogError:
    def test_logs_error_message(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_error("Connection timeout")
            content = log_path.read_text()
            assert "ERROR" in content
            assert "Connection timeout" in content
    
    def test_includes_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            logger.log_error("Test error")
            
            content = log_path.read_text()
            assert content.startswith("[20")


class TestFileWriteFailureHandling:
    def test_continues_console_output_on_file_write_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with patch('builtins.print') as mock_print:
                    logger.log_generated("https://tinyurl.com/test")
                    
                    assert mock_print.call_count == 2
                    calls = [str(call) for call in mock_print.call_args_list]
                    assert any("GENERATED" in call for call in calls)
                    assert any("Failed to write to log file" in call for call in calls)
    
    def test_disables_file_writing_after_first_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with patch('builtins.print') as mock_print:
                    logger.log_generated("https://tinyurl.com/test1")
                    mock_print.reset_mock()
                    logger.log_generated("https://tinyurl.com/test2")
                    
                    assert mock_print.call_count == 1
    
    def test_handles_io_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            with patch('builtins.open', side_effect=IOError("Disk full")):
                with patch('builtins.print') as mock_print:
                    logger.log_error("Test error")
                    
                    calls = [str(call) for call in mock_print.call_args_list]
                    assert any("Failed to write to log file" in call for call in calls)


class TestLogAppendBehavior:
    def test_appends_to_existing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            logger.log_generated("https://tinyurl.com/first")
            logger.log_generated("https://tinyurl.com/second")
            logger.log_generated("https://tinyurl.com/third")
            
            content = log_path.read_text()
            lines = content.strip().split('\n')
            assert len(lines) == 3
            assert "first" in content
            assert "second" in content
            assert "third" in content
    
    def test_preserves_previous_entries_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            
            logger1 = Logger(str(log_path))
            logger1.log_generated("https://tinyurl.com/first")
            
            logger2 = Logger(str(log_path))
            logger2.log_generated("https://tinyurl.com/second")
            
            content = log_path.read_text()
            assert "first" in content
            assert "second" in content


class TestDualOutput:
    def test_all_methods_output_to_both_console_and_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            
            with patch('builtins.print') as mock_print:
                logger.log_generated("https://tinyurl.com/test1")
                logger.log_validation("https://tinyurl.com/test2", True)
                logger.log_redirect("https://tinyurl.com/test3", "https://mega.nz/file")
                logger.log_classification("https://mega.nz/file", "UHQ")
                logger.log_error("Test error message")
                
                assert mock_print.call_count == 5
            
            content = log_path.read_text()
            lines = content.strip().split('\n')
            assert len(lines) == 5
