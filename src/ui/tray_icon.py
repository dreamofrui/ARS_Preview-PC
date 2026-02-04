"""
Tray Icon
System tray icon for Preview-PC Simulator
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from typing import Optional


class TrayIcon(QObject):
    """System tray icon manager"""

    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    pause_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._menu: Optional[QMenu] = None

    def create(self, icon_path: Optional[str] = None) -> None:
        """Create tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # Create icon (use default if none provided)
        if icon_path:
            icon = QIcon(icon_path)
        else:
            # Create a simple colored icon
            from PyQt6.QtGui import QPixmap, QPainter
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.gray)
            icon = QIcon(pixmap)

        self._tray_icon = QSystemTrayIcon(icon)
        self._create_menu()
        self._tray_icon.show()

        # Handle double click
        self._tray_icon.activated.connect(self._on_activated)

    def _create_menu(self) -> None:
        """Create context menu"""
        self._menu = QMenu()

        show_action = QAction("显示窗口", self._menu)
        show_action.triggered.connect(self.show_requested.emit)
        self._menu.addAction(show_action)

        self._menu.addSeparator()

        quit_action = QAction("退出", self._menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(quit_action)

        self._tray_icon.setContextMenu(self._menu)

    def _on_activated(self, reason) -> None:
        """Handle tray icon activation"""
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()

    def set_tooltip(self, text: str) -> None:
        """Set tooltip text"""
        if self._tray_icon:
            self._tray_icon.setToolTip(f"Review PC Simulator - {text}")

    def show_message(self, title: str, message: str) -> None:
        """Show balloon message"""
        if self._tray_icon:
            self._tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )

    def hide_icon(self) -> None:
        """Hide tray icon"""
        if self._tray_icon:
            self._tray_icon.hide()
