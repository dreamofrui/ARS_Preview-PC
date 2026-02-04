"""
Main Window
Primary application window for Preview-PC Simulator
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QMessageBox, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QPixmap

from src.config.config_manager import ConfigManager
from src.config.setup_wizard import SetupWizard
from src.resources.image_loader import ImageLoader
from src.logging.logger import AppLogger
from src.core.batch_manager import BatchManager, BatchState
from src.core.timeout_manager import TimeoutManager
from src.core.key_handler import KeyHandler
from src.ui.grid_widget import GridWidget
from src.ui.big_image_dialog import BigImageDialog
from src.ui.tray_icon import TrayIcon
from src.injectors.lag_injector import LagInjector
from src.injectors.popup_injector import PopupInjector
from src.injectors.crash_injector import CrashInjector


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Review PC")
        self.setMinimumSize(800, 600)
        self.resize(1280, 720)

        # Initialize components
        self._config = ConfigManager()
        self._logger = AppLogger(self._config.get_log_file())
        self._image_loader = ImageLoader()
        self._batch = BatchManager()
        self._timeout = TimeoutManager()
        self._key_handler = KeyHandler(self._batch)
        self._tray = TrayIcon()

        # Injectors
        self._lag_injector = LagInjector(self._batch)
        self._popup_injector = PopupInjector(self)
        self._crash_injector = CrashInjector(self)

        # Big image dialog
        self._big_dialog: Optional[BigImageDialog] = None

        # State
        self._timed_out_indices = set()  # Track which image indices (0-based) have timed out in current batch
        self._current_timeout_image = None  # Store current timeout image
        self._waiting_for_key_after_timeout = False  # True when timeout occurred, waiting for N/M key

        # Countdown timer for timeout display
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._update_countdown)
        self._countdown_timer.start(100)  # Update every 100ms

        # Connect signals
        self._connect_signals()

        # Setup UI
        self._init_ui()

        # Load configuration
        self._load_configuration()

        # Setup tray
        self._tray.create()
        self._tray.show_requested.connect(self.show)
        self._tray.quit_requested.connect(self.close)

        # Log startup
        self._logger.info("Application started")

    def _connect_signals(self) -> None:
        """Connect signals"""
        self._batch.state_changed.connect(self._on_state_changed)
        self._batch.image_changed.connect(self._on_image_changed)
        self._batch.progress_updated.connect(self._on_progress_updated)
        self._batch.batch_completed.connect(self._on_batch_completed)
        self._timeout.timeout_triggered.connect(self._on_timeout)
        self._key_handler.key_processed.connect(self._on_key_processed)

    def _init_ui(self) -> None:
        """Initialize UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Status bar
        self._status_label = QLabel("Ready")
        self._status_label.setFixedHeight(30)
        self._status_label.setStyleSheet("QLabel { padding: 5px; background-color: #1e1e1e; color: white; }")
        layout.addWidget(self._status_label)

        # Grid widget
        self._grid = GridWidget()
        self._grid.image_clicked.connect(self._on_grid_image_clicked)
        layout.addWidget(self._grid)

        # Control panel
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

    def _create_control_panel(self) -> QFrame:
        """Create control panel"""
        panel = QFrame()
        panel.setFixedHeight(180)
        panel.setStyleSheet("""
            QFrame { background-color: #2d2d2d; }
            QLabel { color: white; font-size: 13px; }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
                padding: 6px 18px;
                border-radius: 4px;
                min-width: 70px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:disabled { background-color: #3a3a3a; color: #6a6a6a; }
            QComboBox {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 60px;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                color: white;
                selection-background-color: #5a5a5a;
            }
            QLineEdit {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 150px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(8)

        # Batch settings row
        batch_row = QHBoxLayout()
        batch_row.setSpacing(15)
        batch_row.addWidget(QLabel("批次数量:"))
        self._batch_combo = QComboBox()
        self._batch_combo.addItems([str(i) for i in range(7)])
        self._batch_combo.setCurrentIndex(6)  # Default to 6
        batch_row.addWidget(self._batch_combo)

        # Mode selection
        batch_row.addSpacing(20)
        batch_row.addWidget(QLabel("模式:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["固定模式", "轮询模式"])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        batch_row.addWidget(self._mode_combo)

        batch_row.addStretch()
        layout.addLayout(batch_row)

        # Cycling sequence row (hidden by default)
        sequence_row = QHBoxLayout()
        sequence_row.setSpacing(15)
        sequence_row.addWidget(QLabel("轮询序列:"))
        self._sequence_edit = QLineEdit("1,2,3,4,5,6")
        self._sequence_edit.setEnabled(False)
        sequence_row.addWidget(self._sequence_edit)
        sequence_row.addStretch()
        layout.addLayout(sequence_row)

        # Flow control row
        flow_row = QHBoxLayout()
        flow_row.setSpacing(15)
        self._start_btn = QPushButton("Start")
        self._start_btn.clicked.connect(self._on_start_clicked)
        flow_row.addWidget(self._start_btn)

        self._pause_btn = QPushButton("Pause")
        self._pause_btn.clicked.connect(self._on_pause_clicked)
        self._pause_btn.setEnabled(False)
        flow_row.addWidget(self._pause_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        self._stop_btn.setEnabled(False)
        flow_row.addWidget(self._stop_btn)
        layout.addLayout(flow_row)

        # View control row
        view_row = QHBoxLayout()
        view_row.setSpacing(15)
        self._big_image_btn = QPushButton("Open Big Image")
        self._big_image_btn.clicked.connect(self._open_big_image)
        view_row.addWidget(self._big_image_btn)
        view_row.addStretch()
        layout.addLayout(view_row)

        # Injection row
        inject_row = QHBoxLayout()
        inject_row.setSpacing(15)
        self._lag_btn = QPushButton("Inject Lag")
        self._lag_btn.clicked.connect(self._inject_lag)
        inject_row.addWidget(self._lag_btn)

        self._popup_btn = QPushButton("Inject Popup")
        self._popup_btn.clicked.connect(self._inject_popup)
        inject_row.addWidget(self._popup_btn)

        self._crash_btn = QPushButton("Crash")
        self._crash_btn.clicked.connect(self._inject_crash)
        inject_row.addWidget(self._crash_btn)

        self._hide_btn = QPushButton("Hide")
        self._hide_btn.clicked.connect(self._hide_to_tray)
        inject_row.addWidget(self._hide_btn)
        inject_row.addStretch()
        layout.addLayout(inject_row)

        return panel

    def _load_configuration(self) -> None:
        """Load configuration"""
        if not self._config.load():
            # Show setup wizard
            wizard = SetupWizard(self)
            if wizard.exec() == QDialog.DialogCode.Accepted:
                normal, wait, timeout = wizard.get_config()
                self._config.set('images.normal_dir', str(normal))
                self._config.set('images.wait_image', str(wait))
                self._config.set('images.timeout_dir', str(timeout))
                self._config.save()
            else:
                QMessageBox.warning(self, "Setup Required", "Configuration is required to run.")
                return

        # Load images
        normal_dir = self._config.get_normal_dir()
        wait_image = self._config.get_wait_image()
        timeout_dir = self._config.get_timeout_dir()

        if normal_dir:
            count = self._image_loader.load_normal_images(normal_dir)
            self._logger.info(f"Loaded {count} normal images")

        if wait_image:
            self._image_loader.load_wait_image(wait_image)

        if timeout_dir:
            count = self._image_loader.load_timeout_images(timeout_dir)
            self._logger.info(f"Loaded {count} timeout images")

        # Apply window settings
        if self._config.get('window.remember_position'):
            x = self._config.get('window.last_x', 100)
            y = self._config.get('window.last_y', 100)
            w = self._config.get('window.last_width', 1280)
            h = self._config.get('window.last_height', 720)
            self.setGeometry(x, y, w, h)

        if self._config.get('window.always_on_top'):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # Load batch count
        self._timeout.set_default_duration(self._config.get('timeout.default_duration', 10))

    def _on_state_changed(self, state: str) -> None:
        """Handle state change"""
        self._logger.log_state_change(self._status_label.text(), state)
        self._update_status()
        self._update_buttons()

    def _on_image_changed(self, current: int, total: int) -> None:
        """Handle image change"""
        # Clear waiting flag (but keep timeout image visible)
        self._waiting_for_key_after_timeout = False
        self._update_display()
        self._timeout.start()

    def _on_progress_updated(self, ok: int, ng: int) -> None:
        """Handle progress update"""
        self._update_status()

    def _on_batch_completed(self, batch_num: int, ok: int, ng: int) -> None:
        """Handle batch completion"""
        self._logger.log_batch_complete(batch_num, ok, ng)
        self._show_batch_complete_dialog(batch_num, ok, ng)

    def _on_timeout(self) -> None:
        """Handle timeout - show timeout image and wait for key press"""
        current = self._batch.current_image
        self._logger.log_timeout(current, self._timeout._current_duration, "timeout image")
        self._show_timeout_image()
        # Set flag to wait for user key press - don't advance automatically
        self._waiting_for_key_after_timeout = True
        # Stop the timeout timer so it doesn't trigger again
        self._timeout.stop()
        # Update status to show we're in timeout state
        self._update_status()

    def _on_key_processed(self, detail: str) -> None:
        """Handle key processed"""
        # If we were waiting after timeout, advance the image (counts as NG)
        if self._waiting_for_key_after_timeout:
            self._waiting_for_key_after_timeout = False
            self._batch.process_timeout()
        self._logger.log_key("", detail)
        self._timeout.stop()
        # Restart timeout for next image
        self._timeout.start()

    def _on_grid_image_clicked(self, index: int) -> None:
        """Handle grid image clicked"""
        self._open_big_image()

    def _update_status(self) -> None:
        """Update status bar"""
        state = self._batch.state.value
        batch = self._batch.batch_num
        current = self._batch.current_image
        total = self._batch.batch_count
        ok = self._batch.ok_count
        ng = self._batch.ng_count

        if self._batch.state == BatchState.RUNNING and self._timeout.is_active:
            remaining = self._timeout.remaining
            status = f"Batch {batch} | Image {current}/{total} | {state} | OK:{ok} NG:{ng} | Timeout: {remaining:.1f}s"
        else:
            status = f"Batch {batch} | Image {current}/{total} | {state} | OK:{ok} NG:{ng}"

        self._status_label.setText(status)
        self._tray.set_tooltip(state)

    def _update_display(self) -> None:
        """Update image display"""
        current = self._batch.current_image - 1  # Convert to 0-indexed
        pixmaps = []

        for i in range(self._batch.batch_count):
            if i in self._timed_out_indices and self._current_timeout_image:
                # Timed out images show timeout image
                pixmaps.append(self._current_timeout_image)
            elif i < current:
                # Already processed - show normal image
                pixmaps.append(self._image_loader.get_normal_image(i))
            elif i == current:
                # Current image
                pixmaps.append(self._image_loader.get_normal_image(i))
            else:
                # Future images - show wait image
                pixmaps.append(self._image_loader.get_wait_image())

        self._grid.update_images(pixmaps, current)

        # Sync big dialog if visible
        self._update_big_dialog()

    def _update_buttons(self) -> None:
        """Update button states"""
        state = self._batch.state
        self._start_btn.setEnabled(state == BatchState.IDLE)

        # Pause/Resume button
        if state == BatchState.RUNNING:
            self._pause_btn.setText("Pause")
            self._pause_btn.setEnabled(True)
        elif state == BatchState.PAUSED:
            self._pause_btn.setText("Resume")
            self._pause_btn.setEnabled(True)
        else:
            self._pause_btn.setText("Pause")
            self._pause_btn.setEnabled(False)

        # Stop button - enabled in RUNNING, PAUSED, or WAITING_CONFIRM
        self._stop_btn.setEnabled(state in [BatchState.RUNNING, BatchState.PAUSED, BatchState.WAITING_CONFIRM])

    def _update_countdown(self) -> None:
        """Update countdown display - always show when running"""
        if self._batch.state == BatchState.RUNNING and self._timeout.is_active:
            self._update_status()  # Always update status when timeout is active

    def _on_start_clicked(self) -> None:
        """Handle start button clicked"""
        # Apply cycling mode settings
        is_cycling = self._mode_combo.currentIndex() == 1  # 1 = 轮询模式
        sequence = self._sequence_edit.text() if is_cycling else None
        self._batch.set_cycling_mode(is_cycling, sequence)

        # Get batch count from combo - use exactly what user selected
        count = int(self._batch_combo.currentText())

        self._batch.set_batch_count(count)
        self._batch.start_batch()
        # Reset all states for new batch
        self._timed_out_indices.clear()
        self._current_timeout_image = None
        self._waiting_for_key_after_timeout = False
        self._update_display()
        self._timeout.start()
        self._logger.log_batch_start(self._batch.batch_num, count)

    def _on_mode_changed(self, index: int) -> None:
        """Handle mode selection change"""
        if index == 1:  # 轮询模式
            self._sequence_edit.setEnabled(True)
        else:  # 固定模式
            self._sequence_edit.setEnabled(False)

    def _on_pause_clicked(self) -> None:
        """Handle pause/resume button clicked"""
        if self._batch.state == BatchState.RUNNING:
            self._batch.pause()
            self._timeout.stop()
        elif self._batch.state == BatchState.PAUSED:
            self._batch.resume()
            self._timeout.start()

    def _on_stop_clicked(self) -> None:
        """Handle stop button clicked"""
        self._batch.stop()
        self._timeout.stop()
        self._timed_out_indices.clear()
        self._current_timeout_image = None
        self._waiting_for_key_after_timeout = False

    def _open_big_image(self) -> None:
        """Open big image dialog"""
        if self._big_dialog is None:
            self._big_dialog = BigImageDialog(self)
            # Connect key press signal to handler
            self._big_dialog.key_pressed.connect(self._on_big_dialog_key_press)
        self._big_dialog.show()

        # Update image immediately
        self._update_big_dialog()

    def _on_big_dialog_key_press(self, key: str) -> None:
        """Handle key press from big dialog"""
        # Forward to key handler
        self._key_handler.handle_key(key)

    def _update_big_dialog(self) -> None:
        """Update big dialog image if visible"""
        if self._big_dialog and self._big_dialog.isVisible():
            current = self._batch.current_image - 1
            if current in self._timed_out_indices and self._current_timeout_image:
                pixmap = self._current_timeout_image
            else:
                pixmap = self._image_loader.get_normal_image(current)
            self._big_dialog.set_image(pixmap)

    def _show_timeout_image(self) -> None:
        """Show timeout replacement image"""
        pixmap = self._image_loader.get_random_timeout_image()
        self._current_timeout_image = pixmap
        # Mark current image index as timed out (0-based)
        current = self._batch.current_image - 1
        self._timed_out_indices.add(current)

        # Update big dialog if visible
        if pixmap and self._big_dialog and self._big_dialog.isVisible():
            self._big_dialog.set_image(pixmap)

        # Update grid to show timeout image
        self._update_display()

    def _show_batch_complete_dialog(self, batch_num: int, ok: int, ng: int) -> None:
        """Show batch complete dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Batch Complete")
        msg.setText(f"Batch {batch_num} completed. OK: {ok}, NG: {ng}. Confirm to proceed?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            self._batch.confirm_batch()
            # Auto-start next batch after confirming
            self._on_start_clicked()
        else:
            self._batch.cancel_batch()

    def _inject_lag(self) -> None:
        """Inject lag"""
        duration = self._config.get('lag_duration', 3)
        self._lag_injector.inject(duration)

    def _inject_popup(self) -> None:
        """Inject popup"""
        self._popup_injector.inject()

    def _inject_crash(self) -> None:
        """Inject crash"""
        self._crash_injector.inject()

    def _hide_to_tray(self) -> None:
        """Hide to tray"""
        self.hide()
        self._tray.show_message("Hidden", "Application hidden to tray. Double-click icon to restore.")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press"""
        key = event.text()
        if key in ['N', 'M', 'Enter', 'Esc']:
            self._key_handler.handle_key(key)
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle close event"""
        # Save window position
        self._config.set('window.last_x', self.x())
        self._config.set('window.last_y', self.y())
        self._config.set('window.last_width', self.width())
        self._config.set('window.last_height', self.height())
        self._config.save()

        self._logger.info("Application closing")
        event.accept()
