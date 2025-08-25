# `\gui` Directory Documentation

This directory contains all the front end of the application. Starting from station buttons and frequency slider, to the config dialog and main application.

## `\gui\config_dialog.py` SDR Configuration Dialog Module

### Overview

The `ConfigDialog` class creates a user-friendly interface for detecting, selecting, and configuring SDR devices on a system using the SoapySDR library.

### Key Features

- **Auto-detection**: Scans for connected SDR devices automatically
- **Smart filtering**: Filters out non-SDR devices (like audio devices) 
- **Auto-selection**: Automatically selects and optionally closes when only one SDR device is found
- **Device rescanning**: Manual rescan capability for hot-plugged devices
- **Clean UI**: Modern styling with status indicators and responsive buttons

### Main Functions

#### `__init__(auto_select_single=True, auto_close_delay=500)`
Initializes the dialog with options for automatic single-device selection and timed auto-closing.

#### `setup_ui()`
Creates the user interface with:
- Device selection dropdown
- Status labels with color-coded feedback
- Rescan, Cancel, and Continue buttons
- Modern styling with hover effects

#### `is_sdr_device(device)`
Smart filtering function that identifies genuine SDR devices by checking:
- Driver names (rtlsdr, hackrf, bladerf, etc.)
- Device labels and descriptions for SDR keywords
- Manufacturer information

#### `scan_devices()`
Core scanning function that:
- Enumerates all available devices via SoapySDR
- Filters for SDR-specific devices
- Populates the selection dropdown
- Handles auto-selection for single devices
- Provides user feedback during scanning

#### `accept_selection()` & `get_selected_device()`
Handle device selection and return the chosen SDR device configuration for use by the calling application.


## `\gui\frequency_slider.py` Custom Widget

### Overview

The `FrequencySlider` class extends `QWidget` to create a custom slider with frequency markings, designed for the FM radio application. It provides a more specialized interface than standard Qt sliders.

### Key Features

- **Visual frequency scale**: Shows major (5 MHz) and minor (1 MHz) tick marks
- **Real-time frequency display**: Shows current frequency above the slider handle
- **Precise control**: Rounds to nearest 0.1 MHz increments
- **Custom styling**: Blue handle with shadow effects and white center dot

### Constructor

#### `__init__(current_freq, min_freq=87.5, max_freq=108.0, parent=None)`
- **current_freq**: Initial frequency to display
- **min_freq/max_freq**: Frequency range (defaults to FM radio band 87.5-108.0 MHz)
- Emits `valueChanged(float)` signal when frequency changes

### Main Functions

#### `paintEvent(event)`
Custom drawing method that renders:
- **Track line**: Horizontal line representing frequency range
- **Major ticks**: Every 5 MHz with frequency labels
- **Minor ticks**: Every 1 MHz for finer resolution
- **Slider handle**: Blue circular handle with shadow and center dot
- **Frequency display**: Current frequency text above handle

#### Mouse Event Handlers
- **`mousePressEvent()`**: Initiates dragging on left click
- **`mouseMoveEvent()`**: Updates frequency during drag operations
- **`mouseReleaseEvent()`**: Ends dragging interaction

#### `updateFrequency(x)`
Core logic that:
- Converts mouse X position to frequency value
- Clamps position to valid track bounds
- Calculates frequency ratio and converts to actual frequency
- Rounds to 0.1 MHz precision
- Triggers widget repaint and emits value change signal

#### Public Methods
- **`setValue(freq)`**: Programmatically set frequency
- **`getValue()`**: Get current frequency value

## `\gui\info_window.py` InfoWindow Notification Widget


### Overview

The `InfoWindow` class extends `QWidget` to create floating tooltip-style notifications that don't steal focus from the main application. It's designed for showing brief status messages or alerts.

### Key Features

- **Non-intrusive**: Doesn't grab keyboard focus or interrupt user workflow
- **Auto-positioning**: Appears near the current mouse cursor location
- **Auto-dismiss**: Automatically closes after a configurable timeout
- **Floating design**: Stays on top of other windows with frameless appearance
- **Dark theme**: Styled with dark background and white text for visibility

### Constructor

#### `__init__(message, timeout=3000, parent=None)`
- **message**: Text to display in the notification
- **timeout**: Auto-close delay in milliseconds (default: 3 seconds)
- **parent**: Parent widget (optional)

### Implementation Details

#### Window Configuration
```python
Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
```
- **Tool**: Creates a tool window (lightweight, doesn't appear in taskbar)
- **FramelessWindowHint**: Removes title bar and window decorations
- **WindowStaysOnTopHint**: Keeps window above other windows

#### Focus Behavior
```python
self.setAttribute(Qt.WA_ShowWithoutActivating)
```
Prevents the notification from stealing focus from the currently active window.

#### Styling
- **Dark theme**: `#333333` background with black border
- **Typography**: White text, 12pt font with padding
- **Border radius**: 5px for rounded corners

#### Positioning Logic
```python
mouse_pos = QCursor.pos()
self.move(mouse_pos + QPoint(10, 10))
```
Positions the window 10 pixels offset from the current mouse cursor to avoid blocking content.

#### Auto-Close
```python
QTimer.singleShot(timeout, self.close)
```
Uses a single-shot timer to automatically close the notification after the specified timeout.

## `\gui\scan_thread.py` Scan Thread

### Overview

The `ScannerWorker` class extends `QObject` and is designed to run in a separate thread, scanning through a frequency range while monitoring the FM receiver's scanning state and providing real-time progress updates.

### Key Features

- **Threaded operation**: Runs scanning in background without blocking UI
- **Progress reporting**: Emits current frequency being scanned
- **Graceful stopping**: Can be safely interrupted mid-scan
- **State monitoring**: Waits for FM receiver to complete each frequency step
- **Error handling**: Comprehensive logging and exception handling

### Constructor

#### `__init__(fm_receiver, start_freq, end_freq)`
- **fm_receiver**: FM receiver object with `get_done()` method
- **start_freq**: Starting frequency for scan (Hz)
- **end_freq**: Ending frequency for scan (Hz)
- Initializes scanning parameters and emits initial progress

### Signals

#### `progress = pyqtSignal(float)`
Emitted continuously during scanning with the current frequency being processed.

#### `finished = pyqtSignal(bool)`
Emitted when scanning completes (successfully or via interruption), always with `True` value.

### Main Functions

#### `run()`
Core scanning loop that:
- **Iterates through frequencies**: Steps through 1 MHz increments
- **Monitors receiver state**: Waits for `get_done() == 0` (ready state)
- **Updates progress**: Emits current frequency to UI
- **Handles completion**: Waits for `get_done() == 1` (processing complete)
- **Checks boundaries**: Stops when end frequency is reached
- **Respects interruption**: Checks `_is_running` flag regularly

#### State Monitoring Logic
```python
while self.fm_receiver.get_done() == 0:  # Wait for ready
    QThread.msleep(10)  # CPU-friendly polling

# Process frequency...

while self.fm_receiver.get_done() == 1:  # Wait for completion
    QThread.msleep(10)
```

#### `stop()`
Safely stops the scanning operation by setting the `_is_running` flag to `False`.

### Threading Integration

This worker is designed to be used with `QThread`:
```python
# Typical usage pattern
thread = QThread()
worker = ScannerWorker(fm_receiver, start_freq, end_freq)
worker.moveToThread(thread)

# Connect signals
worker.progress.connect(update_progress_callback)
worker.finished.connect(scan_complete_callback)

# Start scanning
thread.started.connect(worker.run)
thread.start()
```

### Error Handling

- **Exception logging**: All errors are logged with full stack traces
- **Graceful degradation**: Always emits `finished` signal even on error
- **Resource cleanup**: Ensures proper thread termination

## `\gui\station_button.py` Station Button Widget

### Overview

The `StationButton` class extends `QWidget` to create a comprehensive station control interface that combines a main frequency button with delete and record functionality in a single, styled component.

### Key Features

- **Multi-action interface**: Single widget with tune, delete, and record actions
- **Visual state management**: Different appearances for selected and recording states
- **Modern styling**: Rounded corners, hover effects, and color-coded buttons
- **Signal-based communication**: Emits signals for parent widget handling
- **Compact design**: Fixed-width layout optimized for station lists

### Constructor

#### `__init__(frequency_hz, parent=None)`
- **frequency_hz**: Station frequency in Hz (converted to MHz for display)
- Creates three buttons with appropriate styling and signal connections

### Signals

#### `clicked = pyqtSignal(float)`
Emitted when main station button is clicked (for tuning to frequency).

#### `delete_clicked = pyqtSignal(float)`
Emitted when delete button (✕) is clicked.

#### `record_clicked = pyqtSignal(float)`
Emitted when record button (⏺/⏹) is clicked.

### Component Breakdown

#### Main Button
- **Display**: Shows frequency in MHz format (e.g., "101.5 FM")
- **Styling**: Blue border, white background with hover effects
- **Recording indicator**: Shows red dot (🔴) when recording
- **Selection state**: Blue background when selected

#### Delete Button (✕)
- **Size**: Fixed 32x32 pixels
- **Styling**: Red border with white background, red fill on hover
- **Tooltip**: "Delete Station"

#### Record Button (⏺/⏹)
- **Size**: Fixed 32x32 pixels  
- **States**: Record symbol (⏺) or stop symbol (⏹)
- **Styling**: Orange theme, changes to red when recording
- **Tooltip**: "Record Station" or "Stop Recording"

### State Management Methods

#### `set_recording_state(is_recording)`
Updates the record button appearance and main button text:
- **Recording**: Red background, stop symbol (⏹), red dot in main text
- **Not recording**: Orange border, record symbol (⏺), normal text

#### `set_selected_state(is_selected)`
Updates main button styling:
- **Selected**: Blue background with white text
- **Not selected**: White background with dark text

#### Helper Methods
- **`get_freq()`**: Returns frequency in Hz
- **`get_recording()`**: Returns current recording state
- **`_update_main_button_text()`**: Updates main button text with recording indicator

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│  [    101.5 FM    ]  [✕]  [⏺]                  │
│  Main Button         Del   Rec                  │
└─────────────────────────────────────────────────┘
```

- **Main button**: Flexible width (takes most space)
- **Action buttons**: Fixed 32px circles, right-aligned
- **Container**: 260px wide, 66px minimum height


## `\gui\volume_slider.py` Volume Widget

### Overview

The `VolumeSlider` class extends `QWidget` to create a combined volume control that includes both a vertical slider and a text label showing the current volume level.

### Key Features

- **Vertical orientation**: Space-efficient vertical slider design
- **Real-time feedback**: Label updates instantly as slider moves
- **Standard range**: 0-100 volume scale with 50 as default
- **Signal emission**: Notifies parent widgets of volume changes
- **Centered layout**: Label positioned above slider with center alignment

### Constructor

#### `__init__(parent=None)`
- Initializes slider with 0-100 range and 50 default value
- Sets up vertical layout with centered label
- Connects slider changes to update handler

### Components

#### Label
- **Display format**: "Volume: XX" where XX is current value
- **Alignment**: Horizontally centered above slider
- **Updates**: Real-time synchronization with slider value

#### Slider
- **Orientation**: Vertical (`Qt.Vertical`)
- **Range**: 0 (minimum) to 100 (maximum)
- **Default**: 50 (middle position)
- **Style**: Standard Qt slider appearance

### Signals

#### `volumeChanged = pyqtSignal(int)`
Emitted whenever the volume level changes, passing the new volume value (0-100).

### Methods

#### `emitVolumeChanged(value)`
Internal handler that:
- Updates label text with new volume value
- Emits `volumeChanged` signal to notify parent widgets

#### `setVolume(value)`
Programmatically sets the volume level:
```python
volume_widget.setVolume(75)  # Set to 75%
```

#### `getVolume()`
Returns the current volume level:
```python
current_level = volume_widget.getVolume()  # Returns 0-100
```

### Layout Structure

```
    Volume: 50
        │
        ├── 100
        │
        ○   <- Slider handle
        │
        ├── 0
        │
```

The widget uses a vertical layout with the label at the top and slider below, both centered horizontally.

### Usage Example

```python
# Create volume control
volume_control = VolumeSlider()

# Connect to handler
volume_control.volumeChanged.connect(audio_system.set_volume)

# Programmatic control
volume_control.setVolume(80)
current_vol = volume_control.getVolume()
```

## `\gui\main_window.py` FM Application

### Overview

The `MainWindow` class serves as the primary controller for a software-defined radio (SDR) FM receiver application. It integrates GNU Radio flowgraphs with a modern PyQt5 interface, providing three main views: Home (primary controls), Stations (discovered station grid), and Debug (signal analysis tools).

### Key Features

- **Multi-view interface**: Tabbed navigation between Home, Stations, and Debug views
- **Automated scanning**: Background frequency scanning with progress reporting
- **Multi-channel recording**: Record multiple stations simultaneously 
- **RDS support**: Radio Data System information display
- **Real-time visualization**: Spectrum, waterfall, and constellation displays
- **Configuration persistence**: Saves stations, volume, and settings between sessions

### Constructor

#### `__init__(config_path, sdr_device)`
Initializes the complete FM radio system:
- **config_path**: Configuration file location for persistent settings
- **sdr_device**: SDR hardware identifier for GNU Radio flowgraph
- Sets up GNU Radio receiver (`rds_rx` flowgraph)
- Loads saved configuration and creates UI components

### Main Interface Views

#### Home View (`create_home_widget()`)
Primary control interface featuring:
- **Frequency display**: Large current frequency indicator
- **Control buttons**: Mute/Listen, Scan, Record, Previous/Next station
- **Manual tuning**: `FrequencySlider` for direct frequency selection  
- **Volume control**: `VolumeSlider` with real-time adjustment
- **RDS information**: Station identification and metadata
- **Signal strength**: Reception quality indicator

#### Stations View (`create_stations_widget()`)
Scrollable grid of discovered stations:
- **Station buttons**: `StationButton` widgets for each discovered frequency
- **Multi-action controls**: Each button supports tune, delete, and record operations
- **Dynamic updates**: Real-time addition/removal of stations
- **Recording indicators**: Visual feedback for active recordings

#### Debug View (`create_debug_widget()`)
Advanced signal analysis tools:
- **RF controls**: Gain, filter cutoff, and transition width adjustment
- **Tabbed visualizations**: Spectrum analyzer, waterfall display, constellation diagram
- **Audio monitoring**: Time-domain audio signal display
- **RDS debugging**: Raw RDS data and constellation analysis

### Core Functionality

#### Station Discovery (`scan_mode()`)
Automated FM band scanning:
- **Frequency range**: 88-108 MHz FM band coverage
- **Threaded operation**: `ScannerWorker` prevents UI blocking
- **Wideband mode**: Increased sample rate for faster scanning
- **Progress reporting**: Real-time frequency updates during scan
- **Station detection**: Automatic signal strength thresholding

#### Multi-Channel Recording (`multiple_record()`)
Advanced recording capabilities:
- **Simultaneous recordings**: Multiple stations recorded concurrently
- **Frequency validation**: Checks SDR bandwidth limitations
- **Dynamic flowgraph**: Real-time GNU Radio connection management
- **Timestamped files**: Automatic file naming with frequency identification
- **State management**: Recording status tracking per station

#### Audio Management
- **Volume control**: 0-100 scale mapped to dB range
- **Mute functionality**: Independent of volume setting
- **Real-time adjustment**: Immediate audio level changes

### Configuration Management

#### Persistent Settings
- **Station list**: Discovered frequencies saved between sessions
- **Audio settings**: Volume level and mute state
- **Recording directory**: User-selected output folder
- **Window state**: UI layout and selected view

### Signal Processing Integration

#### GNU Radio Flowgraph (`rds_rx`)
- **SDR interface**: Configurable device selection and parameters
- **FM demodulation**: Standard FM broadcast demodulation
- **RDS decoding**: Radio Data System text extraction
- **Audio processing**: Deemphasis filtering and stereo decoding
- **Multi-output**: Supports simultaneous recording streams

#### Real-time Controls
- **Frequency tuning**: Immediate frequency changes
- **Filter adjustment**: Runtime DSP parameter modification
- **Gain control**: RF amplification management
- **Sample rate**: Dynamic bandwidth adjustment for scanning

### Event Handling

#### User Interactions
- **Station navigation**: Previous/Next button cycling through stations
- **Direct tuning**: Frequency slider for manual selection
- **Recording control**: Individual station recording management
- **View switching**: Bottom navigation between interface modes

#### Background Operations
- **Scanning thread**: Non-blocking frequency sweep operation
- **Progress updates**: Real-time scanning status reporting
- **Error handling**: Graceful recovery from hardware/software issues
