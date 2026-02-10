"""
Big Image Dialog
Independent popup window for displaying enlarged images
"""

from typing import Optional
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal


class BigImageDialog(QDialog):
    """Dialog for displaying enlarged image"""

    # Signal to forward key presses to parent
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review PC - Image Viewer (按 ESC 关闭)")
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self._label)
        self.setLayout(layout)

        # Remove WindowStaysOnTopHint so main window buttons remain clickable

    def set_image(self, pixmap: Optional[QPixmap]) -> None:
        """Set image to display"""
        if pixmap is None:
            self._label.setText("No Image")
        else:
            scaled = pixmap.scaled(
                self._label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._label.setPixmap(scaled)

    def resizeEvent(self, event):
        """Handle resize to rescale image"""
        super().resizeEvent(event)
        if self._label.pixmap():
            self.set_image(self._label.pixmap())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press - forward to parent for N/M keys"""
        key = event.text().upper()  # Convert to uppercase for case-insensitive matching
        if key in ['N', 'M', 'ENTER', 'ESC']:
            if key == 'ESC':
                self.close()
            else:
                # Forward key press to parent
                self.key_pressed.emit(key)
        super().keyPressEvent(event)
