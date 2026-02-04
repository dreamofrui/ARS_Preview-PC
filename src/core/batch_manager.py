"""
Batch Manager
Manages batch processing state and logic
"""

from enum import Enum
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal


class BatchState(Enum):
    """Batch processing states"""
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"
    WAITING_CONFIRM = "Waiting Confirm"
    TIMEOUT = "Timeout"


class BatchManager(QObject):
    """Manages batch processing state"""

    state_changed = pyqtSignal(str)  # Emitted when state changes
    image_changed = pyqtSignal(int, int)  # current_index, batch_count
    progress_updated = pyqtSignal(int, int)  # ok_count, ng_count
    batch_completed = pyqtSignal(int, int, int)  # batch_num, ok, ng

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = BatchState.IDLE
        self._batch_num = 0
        self._batch_count = 6
        self._current_image = 0  # 0-indexed
        self._ok_count = 0
        self._ng_count = 0
        self._timeout_count = 0

    @property
    def state(self) -> BatchState:
        """Get current state"""
        return self._state

    @property
    def batch_num(self) -> int:
        """Get current batch number"""
        return self._batch_num

    @property
    def batch_count(self) -> int:
        """Get current batch size"""
        return self._batch_count

    @property
    def current_image(self) -> int:
        """Get current image index (1-indexed for display)"""
        return self._current_image + 1

    @property
    def ok_count(self) -> int:
        """Get OK count"""
        return self._ok_count

    @property
    def ng_count(self) -> int:
        """Get NG count"""
        return self._ng_count

    @property
    def timeout_count(self) -> int:
        """Get timeout count"""
        return self._timeout_count

    def set_batch_count(self, count: int) -> None:
        """Set batch size (0-6)"""
        self._batch_count = max(0, min(6, count))

    def start_batch(self) -> None:
        """Start a new batch"""
        self._batch_num += 1
        self._current_image = 0
        self._set_state(BatchState.RUNNING)
        self.image_changed.emit(1, self._batch_count)

    def pause(self) -> None:
        """Pause batch processing"""
        if self._state == BatchState.RUNNING:
            self._set_state(BatchState.PAUSED)

    def resume(self) -> None:
        """Resume batch processing"""
        if self._state == BatchState.PAUSED:
            self._set_state(BatchState.RUNNING)

    def stop(self) -> None:
        """Stop batch processing"""
        self._batch_num = 0
        self._current_image = 0
        self._ok_count = 0
        self._ng_count = 0
        self._timeout_count = 0
        self._set_state(BatchState.IDLE)
        self.progress_updated.emit(0, 0)

    def process_ok(self) -> bool:
        """Process OK key press"""
        if self._state != BatchState.RUNNING:
            return False

        self._ok_count += 1
        return self._advance_image()

    def process_ng(self) -> bool:
        """Process NG key press"""
        if self._state != BatchState.RUNNING:
            return False

        self._ng_count += 1
        return self._advance_image()

    def process_timeout(self) -> bool:
        """Process timeout (counts as NG)"""
        if self._state != BatchState.RUNNING:
            return False

        self._timeout_count += 1
        self._ng_count += 1
        return self._advance_image()

    def _advance_image(self) -> bool:
        """Advance to next image, return True if batch complete"""
        self._current_image += 1
        self.progress_updated.emit(self._ok_count, self._ng_count)

        if self._current_image >= self._batch_count:
            # Batch complete
            self.batch_completed.emit(self._batch_num, self._ok_count, self._ng_count)
            self._set_state(BatchState.WAITING_CONFIRM)
            return False

        self.image_changed.emit(self._current_image + 1, self._batch_count)
        return True

    def confirm_batch(self) -> None:
        """Confirm batch completion"""
        if self._state == BatchState.WAITING_CONFIRM:
            self._current_image = 0
            self._set_state(BatchState.IDLE)

    def cancel_batch(self) -> None:
        """Cancel batch completion"""
        if self._state == BatchState.WAITING_CONFIRM:
            self._current_image = 0
            self._set_state(BatchState.IDLE)

    def _set_state(self, new_state: BatchState) -> None:
        """Set new state and emit signal"""
        self._state = new_state
        self.state_changed.emit(new_state.value)
