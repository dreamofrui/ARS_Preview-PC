"""
Grid Widget
6-grid image display widget
"""

from typing import List, Optional
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, pyqtSignal


class GridImageLabel(QLabel):
    """Individual image label in grid"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_current = False
        self._is_empty = True
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(200, 150)
        self.setStyleSheet("QLabel { background-color: #2b2b2b; border: 2px solid #3b3b3b; }")

    def set_image(self, pixmap: Optional[QPixmap], is_current: bool = False) -> None:
        """Set image and current state"""
        self._is_empty = pixmap is None
        self._is_current = is_current

        if pixmap is None:
            self.setText("Wait")
            self.setStyleSheet("QLabel { background-color: #2b2b2b; border: 2px solid #3b3b3b; color: #888; }")
        else:
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
            self._update_style()

    def _update_style(self) -> None:
        """Update style based on state"""
        if self._is_current:
            self.setStyleSheet("QLabel { background-color: #2b2b2b; border: 3px solid #00ff00; }")
        else:
            self.setStyleSheet("QLabel { background-color: #2b2b2b; border: 2px solid #3b3b3b; }")

    def set_current(self, is_current: bool) -> None:
        """Set current image highlight"""
        self._is_current = is_current
        if not self._is_empty:
            self._update_style()

    def mouseDoubleClickEvent(self, event):
        """Handle double click to open big image"""
        # self.parent() is GridWidget
        self.parent().open_big_image(self)
        super().mouseDoubleClickEvent(event)


class GridWidget(QWidget):
    """6-grid image display widget"""

    image_clicked = pyqtSignal(int)  # Emitted when image is clicked (index)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._labels: List[GridImageLabel] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI"""
        layout = QGridLayout()
        layout.setSpacing(10)

        # Create 2x3 grid
        for i in range(6):
            label = GridImageLabel(self)
            row = i // 3
            col = i % 3
            layout.addWidget(label, row, col)
            self._labels.append(label)

        self.setLayout(layout)

    def update_images(self, pixmaps: List[Optional[QPixmap]], current_index: int) -> None:
        """Update grid images

        Args:
            pixmaps: List of 6 pixmaps (None for empty/wait)
            current_index: Current image index (0-5)
        """
        for i, label in enumerate(self._labels):
            is_current = (i == current_index)
            pixmap = pixmaps[i] if i < len(pixmaps) else None
            label.set_image(pixmap, is_current)

    def update_current(self, current_index: int) -> None:
        """Update current image highlight"""
        for i, label in enumerate(self._labels):
            label.set_current(i == current_index)

    def open_big_image(self, label: GridImageLabel) -> None:
        """Open big image for clicked label"""
        index = self._labels.index(label)
        self.image_clicked.emit(index)
