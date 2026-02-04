"""
Logger Module
Handles application logging with file and console output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class AppLogger:
    """Application logger with file and console handlers"""

    def __init__(self, log_file: Optional[Path] = None):
        self._logger = logging.getLogger("PreviewPC")
        self._logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self._logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_format)
        self._logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self._logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log info message"""
        self._logger.info(message)

    def debug(self, message: str) -> None:
        """Log debug message"""
        self._logger.debug(message)

    def warning(self, message: str) -> None:
        """Log warning message"""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message"""
        self._logger.error(message)

    def log_key(self, key: str, detail: str) -> None:
        """Log keyboard event"""
        self.info(f"[KEY] {key} pressed - {detail}")

    def log_state_change(self, from_state: str, to_state: str) -> None:
        """Log state change"""
        self.info(f"[STATE] {from_state} -> {to_state}")

    def log_batch_start(self, batch_num: int, count: int) -> None:
        """Log batch start"""
        self.info(f"[BATCH] Batch {batch_num} started - {count} images")

    def log_batch_complete(self, batch_num: int, ok: int, ng: int, timeout: int = 0) -> None:
        """Log batch completion"""
        self.info(f"[BATCH] Batch {batch_num} completed - OK: {ok}, NG: {ng}, Timeout: {timeout}")

    def log_timeout(self, image_index: int, duration: float, replaced_with: str) -> None:
        """Log timeout event"""
        self.warning(f"[TIMEOUT] Image {image_index} timeout after {duration:.1f}s, replaced with {replaced_with}")

    def log_inject(self, injection_type: str, detail: str = "") -> None:
        """Log fault injection"""
        msg = f"[INJECT] {injection_type}"
        if detail:
            msg += f" - {detail}"
        self.info(msg)

    def close(self) -> None:
        """Close all handlers and release file locks"""
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)
