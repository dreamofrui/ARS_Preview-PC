#!/usr/bin/env python3
"""
Preview-PC Simulator - Entry Point
High-fidelity Review PC simulator for ARS AutoGUI testing
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
