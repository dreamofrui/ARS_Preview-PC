"""
Lag Injector
Simulates application lag/freezing
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.core.batch_manager import BatchManager, BatchState


class LagInjector(QObject):
    """Injects lag into the application

    Simulates UI freezing while timeout continues running.
    This tests that automation scripts handle frozen UI correctly.
    """

    lag_started = pyqtSignal()  # Emitted when lag starts
    lag_ended = pyqtSignal()    # Emitted when lag ends

    def __init__(self, batch_manager: BatchManager, parent=None):
        super().__init__(parent)
        self._batch = batch_manager
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_lag_end)

        self._is_lagging = False
        self._previous_state: BatchState = BatchState.IDLE

    def inject(self, duration: float = 3.0) -> None:
        """Inject lag for specified duration (seconds)

        Simulates UI freeze while timeout continues running.
        This tests that automation scripts handle frozen UI correctly.
        """
        if self._is_lagging:
            return  # Already lagging

        self._is_lagging = True
        self._previous_state = self._batch.state

        # Set to PAUSED state to prevent user interaction during lag
        # But timeout timer will continue (handled by main_window)
        if self._batch.state == BatchState.RUNNING:
            self._batch.pause()

        self._timer.start(int(duration * 1000))
        self.lag_started.emit()  # Notify UI to show lag state

    def cancel(self) -> None:
        """Cancel lag injection"""
        if not self._is_lagging:
            return
        self._timer.stop()
        self._on_lag_end()

    def _on_lag_end(self) -> None:
        """Handle lag end"""
        self._is_lagging = False

        # Restore previous state
        if self._previous_state == BatchState.RUNNING:
            self._batch.resume()
        elif self._previous_state == BatchState.PAUSED:
            self._batch._set_state(BatchState.PAUSED)
        else:
            self._batch._set_state(BatchState.IDLE)

        self.lag_ended.emit()  # Notify UI lag ended
