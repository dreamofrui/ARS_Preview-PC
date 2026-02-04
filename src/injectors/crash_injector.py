"""
Crash Injector
Simulates application crash dialog
"""

from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import Qt


class CrashInjector:
    """Injects fake crash dialog"""

    def __init__(self, parent: QWidget):
        self._parent = parent

    def inject(self) -> None:
        """Show crash dialog"""
        msg = QMessageBox(self._parent)
        msg.setWindowTitle("Review PC has stopped working")
        msg.setText("Review PC has encountered a problem and needs to close.")
        msg.setInformativeText("We are sorry for the inconvenience.")
        msg.setIcon(QMessageBox.Icon.Critical)

        # Windows-style buttons
        close_button = msg.addButton("Close the program", QMessageBox.ButtonRole.ActionRole)
        debug_button = msg.addButton("Debug", QMessageBox.ButtonRole.ActionRole)

        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.exec()
