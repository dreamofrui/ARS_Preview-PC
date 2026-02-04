"""
Tests for image loader
"""

import pytest
from pathlib import Path
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication
import sys

from src.resources.image_loader import ImageLoader


@pytest.fixture
def app():
    """Create QApplication for tests"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


@pytest.fixture
def temp_images(tmp_path):
    """Create temporary test images"""
    # Create test directories
    normal_dir = tmp_path / "normal"
    timeout_dir = tmp_path / "timeout"
    normal_dir.mkdir()
    timeout_dir.mkdir()

    # Create simple test images (1x1 pixel) - valid minimal PNG
    valid_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0'
        b'\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    for i in range(3):
        (normal_dir / f"test_{i}.png").write_bytes(valid_png)
        (timeout_dir / f"timeout_{i}.png").write_bytes(valid_png)

    wait_image = tmp_path / "wait.png"
    wait_image.write_bytes(valid_png)

    return {
        'normal_dir': normal_dir,
        'timeout_dir': timeout_dir,
        'wait_image': wait_image
    }


def test_load_normal_images(app, temp_images):
    """Test loading normal images"""
    loader = ImageLoader()
    count = loader.load_normal_images(temp_images['normal_dir'])

    assert count == 3
    assert loader.normal_image_count == 3


def test_load_wait_image(app, temp_images):
    """Test loading wait image"""
    loader = ImageLoader()
    result = loader.load_wait_image(temp_images['wait_image'])

    assert result is True
    assert loader.get_wait_image() is not None


def test_get_normal_image_with_cycling(app, temp_images):
    """Test getting normal images with cycling"""
    loader = ImageLoader()
    loader.load_normal_images(temp_images['normal_dir'])

    # Should cycle through images
    img1 = loader.get_normal_image(0)
    img2 = loader.get_normal_image(3)  # Should cycle back to 0
    assert img1 is not None
    assert img2 is not None


def test_get_random_timeout_image(app, temp_images):
    """Test getting random timeout image"""
    loader = ImageLoader()
    loader.load_timeout_images(temp_images['timeout_dir'])

    img = loader.get_random_timeout_image()
    assert img is not None
