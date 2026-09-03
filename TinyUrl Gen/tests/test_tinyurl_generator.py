import pytest
import re
from src.tinyurl_generator import TinyURLGenerator
from src.logger import Logger
import tempfile
from pathlib import Path


class TestTinyURLGeneratorInitialization:
    def test_init_with_logger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            assert generator.logger == logger


class TestTinyURLGeneratorValidation:
    def test_empty_pattern_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            with pytest.raises(ValueError, match="Pattern cannot be empty"):
                generator.generate_candidates("", 5)
    
    def test_invalid_regex_pattern_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            with pytest.raises(ValueError, match="Invalid regex pattern"):
                generator.generate_candidates("[invalid(", 5)
    
    def test_negative_count_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            with pytest.raises(ValueError, match="Count must be positive"):
                generator.generate_candidates(r"https://tinyurl\.com/\w{7}", -1)
    
    def test_zero_count_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            with pytest.raises(ValueError, match="Count must be positive"):
                generator.generate_candidates(r"https://tinyurl\.com/\w{7}", 0)


class TestTinyURLGeneratorPatternConformance:
    def test_generates_urls_matching_pattern(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            pattern = r"https://tinyurl\.com/[a-z0-9]{7}"
            candidates = generator.generate_candidates(pattern, 10)
            
            compiled_pattern = re.compile(pattern)
            for candidate in candidates:
                assert compiled_pattern.match(candidate)
    
    def test_generates_exact_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            pattern = r"https://tinyurl\.com/[a-zA-Z0-9]{6}"
            candidates = generator.generate_candidates(pattern, 15)
            assert len(candidates) == 15
    
    def test_logs_each_generated_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = Logger(str(log_path))
            generator = TinyURLGenerator(logger)
            pattern = r"https://tinyurl\.com/\w{8}"
            candidates = generator.generate_candidates(pattern, 5)
            
            log_content = log_path.read_text()
            for candidate in candidates:
                assert candidate in log_content
                assert "GENERATED" in log_content


class TestTinyURLGeneratorBatchSize:
    def test_single_candidate_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            pattern = r"https://tinyurl\.com/[a-z0-9]{7}"
            candidates = generator.generate_candidates(pattern, 1)
            assert len(candidates) == 1
    
    def test_large_batch_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = Logger(str(Path(tmpdir) / "test.log"))
            generator = TinyURLGenerator(logger)
            pattern = r"https://tinyurl\.com/[a-z0-9]{7}"
            candidates = generator.generate_candidates(pattern, 100)
            assert len(candidates) == 100
