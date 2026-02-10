"""Test tray icon import issue"""
import sys
from PyQt6.QtWidgets import QApplication

# Create QApplication first (required for Qt widgets)
app = QApplication(sys.argv)

# Try to import and create TrayIcon
try:
    from src.ui.tray_icon import TrayIcon
    tray = TrayIcon()
    tray.create()
    print("[OK] TrayIcon created successfully")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Test passed!")
