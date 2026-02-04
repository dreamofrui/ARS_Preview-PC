"""
Popup Injector
Injects distracting popup windows
"""

import random
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QPoint


class PopupInjector:
    """Injects distracting popup windows"""

    TITLES = [
        "License Warning",
        "System Alert",
        "Connection Lost",
        "Update Available",
        "Storage Full",
        "Memory Warning"
    ]

    MESSAGES = [
        "Your license may be invalid. Please check your credentials.",
        "A system error has occurred. Check logs for details.",
        "Connection to server has been lost. Retrying...",
        "A new update is available. Would you like to install?",
        "Your disk space is running low. Free up space now.",
        "Memory usage is high. Close some applications."
    ]

    def __init__(self, parent: QWidget):
        self._parent = parent

    def inject(self) -> None:
        """Inject a random popup"""
        title = random.choice(self.TITLES)
        message = random.choice(self.MESSAGES)

        msg = QMessageBox(self._parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Random position near parent window
        if self._parent:
            parent_geo = self._parent.geometry()
            x = parent_geo.x() + random.randint(50, 200)
            y = parent_geo.y() + random.randint(50, 200)
            msg.move(QPoint(x, y))

        msg.show()
