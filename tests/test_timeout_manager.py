"""
Tests for timeout manager
"""

import pytest
import time
from PyQt6.QtWidgets import QApplication
import sys
from src.core.timeout_manager import TimeoutManager


@pytest.fixture
def app():
    """Create QApplication for tests"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


def test_timeout_manager_initial_state(app):
    """Test initial state"""
    manager = TimeoutManager()
    assert not manager.is_active
    assert manager.remaining == 0.0


def test_timeout_manager_start(app):
    """Test starting timer"""
    manager = TimeoutManager()
    manager.set_default_duration(1.0)
    manager.start()

    assert manager.is_active
    assert manager.remaining > 0


def test_timeout_manager_stop(app):
    """Test stopping timer"""
    manager = TimeoutManager()
    manager.start()
    manager.stop()

    assert not manager.is_active


def test_timeout_manager_trigger(app, qtbot):
    """Test timeout trigger"""
    manager = TimeoutManager()
    manager.set_default_duration(0.1)

    timeout_triggered = False

    def on_timeout():
        nonlocal timeout_triggered
        timeout_triggered = True

    manager.timeout_triggered.connect(on_timeout)
    manager.start()

    qtbot.wait(200)

    assert timeout_triggered
    assert not manager.is_active
