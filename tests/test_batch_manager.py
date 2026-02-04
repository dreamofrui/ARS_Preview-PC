"""
Tests for batch manager
"""

import pytest
from PyQt6.QtWidgets import QApplication
import sys
from src.core.batch_manager import BatchManager, BatchState


@pytest.fixture
def app():
    """Create QApplication for tests"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


def test_batch_manager_initial_state(app):
    """Test initial state"""
    manager = BatchManager()
    assert manager.state == BatchState.IDLE
    assert manager.batch_num == 0
    assert manager.ok_count == 0
    assert manager.ng_count == 0


def test_start_batch(app):
    """Test starting a batch"""
    manager = BatchManager()
    manager.set_batch_count(3)
    manager.start_batch()

    assert manager.state == BatchState.RUNNING
    assert manager.batch_num == 1
    assert manager.current_image == 1


def test_process_ok(app):
    """Test processing OK"""
    manager = BatchManager()
    manager.set_batch_count(3)
    manager.start_batch()

    manager.process_ok()
    assert manager.ok_count == 1
    assert manager.current_image == 2


def test_batch_completion(app):
    """Test batch completion"""
    manager = BatchManager()
    manager.set_batch_count(2)
    manager.start_batch()

    manager.process_ok()  # Image 1 -> 2
    assert manager.state == BatchState.RUNNING

    manager.process_ok()  # Image 2 -> complete
    assert manager.state == BatchState.WAITING_CONFIRM


def test_confirm_batch(app):
    """Test confirming batch"""
    manager = BatchManager()
    manager.set_batch_count(1)
    manager.start_batch()

    manager.process_ok()
    assert manager.state == BatchState.WAITING_CONFIRM

    manager.confirm_batch()
    assert manager.state == BatchState.IDLE


def test_pause_resume(app):
    """Test pause and resume"""
    manager = BatchManager()
    manager.start_batch()

    manager.pause()
    assert manager.state == BatchState.PAUSED

    manager.resume()
    assert manager.state == BatchState.RUNNING
