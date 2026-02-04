"""
Tests for configuration manager
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.config.config_manager import ConfigManager


@pytest.fixture
def temp_config():
    """Create a temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    yield config_path
    Path(config_path).unlink(missing_ok=True)


def test_config_manager_creates_default(temp_config):
    """Test that config manager creates default config"""
    manager = ConfigManager(temp_config)
    assert manager.get('batch.default_count') == 6
    assert manager.get('timeout.default_duration') == 10


def test_config_manager_load_existing(temp_config):
    """Test loading existing configuration"""
    # Create config file
    test_config = {
        "batch": {"default_count": 3},
        "timeout": {"default_duration": 15}
    }
    with open(temp_config, 'w') as f:
        json.dump(test_config, f)

    manager = ConfigManager(temp_config)
    manager.load()

    assert manager.get('batch.default_count') == 3
    assert manager.get('timeout.default_duration') == 15


def test_config_manager_save_and_load(temp_config):
    """Test saving and loading configuration"""
    manager = ConfigManager(temp_config)
    manager.set('batch.default_count', 4)
    manager.save()

    # Load into new manager
    manager2 = ConfigManager(temp_config)
    manager2.load()
    assert manager2.get('batch.default_count') == 4


def test_config_manager_is_configured(temp_config):
    """Test is_configured check"""
    manager = ConfigManager(temp_config)
    assert not manager.is_configured

    manager.set('images.normal_dir', '/path/to/normal')
    manager.set('images.wait_image', '/path/to/wait.png')
    manager.set('images.timeout_dir', '/path/to/timeout')

    assert manager.is_configured
