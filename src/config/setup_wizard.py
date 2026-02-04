"""
Setup Wizard
First-run configuration wizard for Preview-PC Simulator
"""

from pathlib import Path
from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt


class SetupWizard(QDialog):
    """First-run configuration wizard"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview-PC Setup Wizard")
        self.setModal(True)
        self.setFixedSize(500, 350)

        self.normal_dir: Optional[Path] = None
        self.wait_image: Optional[Path] = None
        self.timeout_dir: Optional[Path] = None

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Preview-PC Setup Wizard")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Welcome to Preview-PC Simulator!\n\n"
            "Please configure the following paths to get started:"
        )
        layout.addWidget(instructions)

        layout.addSpacing(20)

        # Normal images directory
        layout.addWidget(QLabel("Normal Images Directory:"))
        normal_layout = QHBoxLayout()
        self.normal_input = QLineEdit()
        self.normal_input.setPlaceholderText("Select folder with normal product images...")
        normal_layout.addWidget(self.normal_input)
        normal_btn = QPushButton("Browse...")
        normal_btn.clicked.connect(self._select_normal_dir)
        normal_layout.addWidget(normal_btn)
        layout.addLayout(normal_layout)

        layout.addSpacing(10)

        # Wait image
        layout.addWidget(QLabel("Wait Image:"))
        wait_layout = QHBoxLayout()
        self.wait_input = QLineEdit()
        self.wait_input.setPlaceholderText("Select the wait/placeholder image...")
        wait_layout.addWidget(self.wait_input)
        wait_btn = QPushButton("Browse...")
        wait_btn.clicked.connect(self._select_wait_image)
        wait_layout.addWidget(wait_btn)
        layout.addLayout(wait_layout)

        layout.addSpacing(10)

        # Timeout images directory
        layout.addWidget(QLabel("Timeout Images Directory:"))
        timeout_layout = QHBoxLayout()
        self.timeout_input = QLineEdit()
        self.timeout_input.setPlaceholderText("Select folder with timeout replacement images...")
        timeout_layout.addWidget(self.timeout_input)
        timeout_btn = QPushButton("Browse...")
        timeout_btn.clicked.connect(self._select_timeout_dir)
        timeout_layout.addWidget(timeout_btn)
        layout.addLayout(timeout_layout)

        layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Finish Setup")
        confirm_btn.clicked.connect(self._finish_setup)
        confirm_btn.setStyleSheet("font-weight: bold;")
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(confirm_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _select_normal_dir(self) -> None:
        """Select normal images directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Normal Images Directory"
        )
        if path:
            self.normal_dir = Path(path)
            self.normal_input.setText(path)

    def _select_wait_image(self) -> None:
        """Select wait image"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Wait Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.wait_image = Path(path)
            self.wait_input.setText(path)

    def _select_timeout_dir(self) -> None:
        """Select timeout images directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Timeout Images Directory"
        )
        if path:
            self.timeout_dir = Path(path)
            self.timeout_input.setText(path)

    def _finish_setup(self) -> None:
        """Validate and finish setup"""
        errors = []

        if not self.normal_dir or not self.normal_dir.exists():
            errors.append("Please select a valid normal images directory")

        if not self.wait_image or not self.wait_image.exists():
            errors.append("Please select a valid wait image")

        if not self.timeout_dir or not self.timeout_dir.exists():
            errors.append("Please select a valid timeout images directory")

        if errors:
            QMessageBox.warning(
                self, "Setup Error",
                "\n".join(errors)
            )
            return

        self.accept()

    def get_config(self) -> Tuple[Path, Path, Path]:
        """Get configured paths"""
        return self.normal_dir, self.wait_image, self.timeout_dir
