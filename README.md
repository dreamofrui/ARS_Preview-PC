# Preview-PC Simulator

A high-fidelity simulator for the Review PC application, designed for testing ARS AutoGUI automation scripts.

## Features

- **6-grid view** mimicking the real Review PC interface
- **Dynamic batch sizes** (0-6 images per batch)
- **Independent big image popup** for detailed viewing
- **Timeout detection** with automatic image replacement
- **Fault injection** capabilities:
  - Lag injection
  - Popup injection
  - Crash simulation
  - Hide to tray
- **System tray integration**
- **Comprehensive logging**

## Installation

1. Ensure Python 3.10+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## First Run

On first run, the setup wizard will prompt for:
- Normal images directory
- Wait image
- Timeout images directory

## Usage

### Basic Controls

- **Start**: Begin a batch with specified image count
- **Pause**: Pause the current batch
- **Stop**: Stop and reset
- **N**: Mark current image as OK, move to next
- **M**: Mark current image as NG, move to next
- **Enter/Esc**: Confirm/cancel batch completion dialog

### Fault Injection

- **Inject Lag**: Simulates 3-second lag (configurable)
- **Inject Popup**: Shows random distraction popup
- **Crash**: Shows fake crash dialog
- **Hide**: Hides application to system tray

### Configuration

Edit `config.json` to customize:
- Image paths
- Timeout durations
- Window behavior
- Logging options

## Development

Run tests:
```bash
pytest tests/ -v
```

Run application:
```bash
python main.py
```

## Building Executable

```bash
pyinstaller --onefile --windowed --name "Review-PC-Simulator" main.py
```

## License

Internal use only.
