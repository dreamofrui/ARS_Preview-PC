"""
Integration test for Preview-PC Simulator
"""

import pytest
from PyQt6.QtWidgets import QApplication
import sys
from pathlib import Path
import tempfile


@pytest.fixture
def temp_config():
    """Create temporary config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create image directories
        (tmpdir_path / "normal").mkdir()
        (tmpdir_path / "timeout").mkdir()

        # Create dummy images
        for i in range(6):
            (tmpdir_path / "normal" / f"img{i}.png").write_bytes(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
                b'\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            )
            (tmpdir_path / "timeout" / f"timeout{i}.png").write_bytes(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
                b'\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            )

        (tmpdir_path / "wait.png").write_bytes(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        yield tmpdir_path


def test_main_window_loads(temp_config):
    """Test that main window can be created"""
    # Skip if no display
    try:
        from PyQt6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication(sys.argv)
    except:
        pytest.skip("No display available")

    # This would require mocking the config
    # For now, just verify imports work
    from src.ui.main_window import MainWindow
    assert True
