# FM Receiver Application

This repository contains the entry point and main application coordinator for the **FM Receiver Application**, a Qt-based SDR FM radio receiver. The project integrates GUI components, SDR flowgraphs, and configuration utilities.

---

## Project Structure

```
.
├── main.py   # Application entry point
├── app.py    # Main FM Receiver Application class
.
.
.
```

The following sections document the purpose and functionality of each file.

---

## `main.py`

**Purpose:**
`main.py` serves as the application entry point. It parses command-line arguments, configures logging, initializes the Qt application, displays the configuration dialog, and launches the main FM receiver window.

### Functions

#### `parse_arguments()`

* **Description:** Parses command-line arguments for the application.
* **Arguments:**

  * `--debug` (flag): Enables debug-level logging.
  * `--config <path>` (string): Path to an external configuration file.
* **Returns:** `argparse.Namespace` containing parsed arguments.

#### `main()`

* **Description:** Main execution flow of the application.
* **Steps performed:**

  1. Parse command-line arguments.
  2. Configure logging using `setup_logging()`.
  3. Initialize a Qt `QApplication`.
  4. Display the `ConfigDialog` to allow the user to select an SDR device.
  5. If the dialog is accepted, extract the selected SDR device driver and serial.
  6. Instantiate the `FMReceiverApp` with the configuration path and device.
  7. Display the main application window.
  8. Enter the Qt event loop.
* **Exit Conditions:**

  * If the configuration dialog is canceled, the application terminates with `sys.exit(0)`.
  * Otherwise, it runs until the Qt event loop exits.

---

## `app.py`

**Purpose:**
`app.py` defines the `FMReceiverApp` class, which coordinates the main window and serves as the application-level controller.

### Classes

#### `FMReceiverApp`

* **Description:** Main application coordinator responsible for creating and managing the GUI main window.
* **Constructor (`__init__`)**

  * **Parameters:**

    * `config_path` (string, optional): Path to a configuration file for the receiver.
    * `selected_device` (string/int, optional): SDR device identifier (driver and serial).
  * **Behavior:** Initializes the `MainWindow` with the provided configuration path and selected device. Logs application initialization events.
* **Methods:**

  * `show()`

    * **Description:** Displays the main application window.
    * **Returns:** None.

---

## Execution Flow

1. The application is started via `main.py`.
2. Command-line arguments are parsed and logging is configured.
3. A Qt application instance is created.
4. The user selects an SDR device in the configuration dialog.
5. If a device is selected, `FMReceiverApp` is instantiated with the configuration and device details.
6. The main window is displayed and the Qt event loop begins.

---

## Dependencies

* Python 3.8+
* `qtpy` for Qt GUI components
* GNU Radio SDR flowgraphs (e.g., `flowgraphs/rds_rx_epy_block_0`)
* Logging utilities under `utils/`
* GUI modules under `gui/` (e.g., `main_window`, `config_dialog`)
