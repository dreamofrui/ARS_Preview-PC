"""
Lag Injector
Simulates application lag/freezing
"""

from PyQt6.QtCore import QObject, QTimer
from src.core.batch_manager import BatchManager, BatchState


class LagInjector(QObject):
    """Injects lag into the application"""

    def __init__(self, batch_manager: BatchManager, parent=None):
        super().__init__(parent)
        self._batch = batch_manager
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_lag_end)

        self._previous_state: BatchState = BatchState.IDLE

    def inject(self, duration: float = 3.0) -> None:
        """Inject lag for specified duration (seconds)"""
        self._previous_state = self._batch.state
        self._batch._set_state(BatchState.PAUSED)  # Internally set to pause but show lag
        self._timer.start(int(duration * 1000))

    def cancel(self) -> None:
        """Cancel lag injection"""
        self._timer.stop()
        self._on_lag_end()

    def _on_lag_end(self) -> None:
        """Handle lag end"""
        # Restore previous state
        if self._previous_state == BatchState.RUNNING:
            self._batch.resume()
        elif self._previous_state == BatchState.IDLE:
            self._batch._set_state(BatchState.IDLE)
