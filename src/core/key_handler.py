"""
Key Handler
Handles keyboard input and routes to appropriate handlers
"""

from PyQt6.QtCore import QObject, pyqtSignal
from src.core.batch_manager import BatchManager, BatchState


class KeyHandler(QObject):
    """Handles keyboard input"""

    key_processed = pyqtSignal(str)  # Emitted when key is processed

    def __init__(self, batch_manager: BatchManager, parent=None):
        super().__init__(parent)
        self._batch = batch_manager

    def handle_key(self, key: str) -> bool:
        """Handle keyboard input

        Returns True if key was processed
        """
        state = self._batch.state
        print(f"[DEBUG] handle_key: key={key}, state={state.value}")

        # Priority 1: Waiting confirm (Enter/Esc only)
        if state == BatchState.WAITING_CONFIRM:
            if key == "Enter":
                self._batch.confirm_batch()
                self.key_processed.emit("Enter - Batch confirmed")
                return True
            elif key == "Esc":
                self._batch.cancel_batch()
                self.key_processed.emit("Esc - Batch cancelled")
                return True
            return False

        # Priority 2: Paused - ignore all
        if state == BatchState.PAUSED:
            return False

        # Priority 3: Running - handle N/M
        if state == BatchState.RUNNING:
            if key == "N":
                result = self._batch.process_ok()
                detail = f"Image {self._batch.current_image - 1} -> {self._batch.current_image}, OK count: {self._batch.ok_count}"
                self.key_processed.emit(f"N - {detail}")
                return True
            elif key == "M":
                result = self._batch.process_ng()
                detail = f"Image {self._batch.current_image - 1} -> {self._batch.current_image}, NG count: {self._batch.ng_count}"
                self.key_processed.emit(f"M - {detail}")
                return True

        print(f"[DEBUG] handle_key: key NOT processed, state={state.value}")
        return False
