"""
Tests for logger
"""

import pytest
import tempfile
from pathlib import Path
from src.logging.logger import AppLogger


@pytest.fixture
def temp_log():
    """Create temporary log file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_path = f.name
    yield log_path
    Path(log_path).unlink(missing_ok=True)


def test_logger_creates_file(temp_log):
    """Test that logger creates log file"""
    logger = AppLogger(Path(temp_log))
    logger.info("Test message")
    logger.close()

    assert Path(temp_log).exists()
    content = Path(temp_log).read_text()
    assert "Test message" in content


def test_logger_key_format(temp_log):
    """Test key event logging format"""
    logger = AppLogger(Path(temp_log))
    logger.log_key("N", "Image 1 -> 2, OK count: 1")
    logger.close()

    content = Path(temp_log).read_text()
    assert "[KEY]" in content
    assert "N pressed" in content


def test_logger_batch_format(temp_log):
    """Test batch logging format"""
    logger = AppLogger(Path(temp_log))
    logger.log_batch_complete(1, 4, 2, 0)
    logger.close()

    content = Path(temp_log).read_text()
    assert "[BATCH]" in content
    assert "OK: 4" in content
    assert "NG: 2" in content
