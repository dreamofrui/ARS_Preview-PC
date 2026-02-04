"""
Big Image Dialog
Independent popup window for displaying enlarged images
"""

from typing import Optional
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class BigImageDialog(QDialog):
    """Dialog for displaying enlarged image"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review PC - Image Viewer")
        self.setMinimumSize(800, 600)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self._label)
        self.setLayout(layout)

        # Always stay on top
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowType.WindowStaysOnTopHint
        )

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

    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
