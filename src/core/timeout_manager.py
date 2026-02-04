"""
Timeout Manager
Manages image timeout detection and replacement
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from typing import Optional


class TimeoutManager(QObject):
    """Manages timeout detection for images"""

    timeout_triggered = pyqtSignal()  # Emitted when timeout occurs

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

        self._default_duration = 10.0  # seconds
        self._current_duration = 10.0
        self._start_time: Optional[float] = None
        self._is_active = False

    def set_default_duration(self, seconds: float) -> None:
        """Set default timeout duration"""
        self._default_duration = max(0.1, seconds)

    def set_duration(self, seconds: float) -> None:
        """Set timeout duration for current image"""
        self._current_duration = max(0.1, seconds)

    def start(self) -> None:
        """Start timeout timer"""
        self._current_duration = self._default_duration
        self._start_time = 0  # Will be set by elapsed property
        self._timer.start(int(self._current_duration * 1000))
        self._is_active = True

    def start_with_duration(self, seconds: float) -> None:
        """Start timer with specific duration"""
        self._current_duration = max(0.1, seconds)
        self._timer.start(int(self._current_duration * 1000))
        self._is_active = True
        self._start_time = 0

    def stop(self) -> None:
        """Stop timeout timer"""
        self._timer.stop()
        self._is_active = False
        self._start_time = None

    def reset(self) -> None:
        """Reset timeout timer"""
        self.stop()
        self.start()

    @property
    def is_active(self) -> bool:
        """Check if timeout is active"""
        return self._is_active

    @property
    def remaining(self) -> float:
        """Get remaining time in seconds"""
        if not self._is_active:
            return 0.0
        return self._timer.remainingTime() / 1000.0

    @property
    def elapsed(self) -> float:
        """Get elapsed time since start"""
        if not self._is_active or self._start_time is None:
            return 0.0
        return self._current_duration - self.remaining

    def _on_timeout(self) -> None:
        """Handle timeout"""
        self._is_active = False
        self.timeout_triggered.emit()
