"""
Tests for timeout manager
"""

import pytest
from PyQt6.QtWidgets import QApplication
import sys
from src.core.timeout_manager import TimeoutManager, DEFAULT_TIMEOUT, MIN_DURATION


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


def test_set_default_duration(app):
    """Test setting default duration"""
    manager = TimeoutManager()
    manager.set_default_duration(5.0)
    manager.start()

    assert manager.is_active
    assert manager.remaining > 0


def test_set_default_duration_clamps_to_minimum(app):
    """Test that default duration is clamped to minimum"""
    manager = TimeoutManager()
    manager.set_default_duration(0.01)  # Below MIN_DURATION

    manager.start()

    # Should be clamped to MIN_DURATION
    assert manager.is_active
    assert manager.remaining >= MIN_DURATION


def test_set_duration(app):
    """Test setting duration for current image"""
    manager = TimeoutManager()
    manager.set_duration(2.0)
    manager.start_with_duration(2.0)

    assert manager.is_active
    assert manager.remaining > 0


def test_set_duration_clamps_to_minimum(app):
    """Test that duration is clamped to minimum"""
    manager = TimeoutManager()
    manager.start_with_duration(0.01)  # Below MIN_DURATION

    assert manager.is_active
    assert manager.remaining >= MIN_DURATION


def test_start_with_duration(app):
    """Test starting timer with specific duration"""
    manager = TimeoutManager()
    manager.start_with_duration(1.5)

    assert manager.is_active
    assert manager.remaining > 0
    assert manager.remaining <= 1.5


def test_reset(app):
    """Test resetting timer"""
    manager = TimeoutManager()
    manager.set_default_duration(1.0)
    manager.start()

    # Wait a bit
    import time
    time.sleep(0.1)

    initial_remaining = manager.remaining
    manager.reset()

    assert manager.is_active
    # After reset, remaining should be close to full duration
    assert manager.remaining > initial_remaining


def test_remaining_property(app):
    """Test remaining time property"""
    manager = TimeoutManager()
    manager.set_default_duration(1.0)
    manager.start()

    remaining = manager.remaining
    assert remaining > 0
    assert remaining <= 1.0

    # After stopping, remaining should be 0
    manager.stop()
    assert manager.remaining == 0.0


def test_elapsed_property(app):
    """Test elapsed time property"""
    manager = TimeoutManager()
    manager.set_default_duration(1.0)
    manager.start()

    import time
    time.sleep(0.1)

    elapsed = manager.elapsed
    assert elapsed > 0
    assert elapsed < 1.0

    # After stopping, elapsed should be 0
    manager.stop()
    assert manager.elapsed == 0.0


def test_elapsed_property_accuracy(app):
    """Test elapsed property accuracy"""
    manager = TimeoutManager()
    manager.start_with_duration(1.0)

    import time
    time.sleep(0.2)

    elapsed = manager.elapsed
    # Elapsed should be approximately 0.2 seconds
    assert 0.15 < elapsed < 0.3


def test_constants_defined():
    """Test that constants are properly defined"""
    assert DEFAULT_TIMEOUT == 10.0
    assert MIN_DURATION == 0.1
