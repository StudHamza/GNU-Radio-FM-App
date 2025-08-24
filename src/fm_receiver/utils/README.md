#  `Utils/` Directory Documentation

##  Purpose

This directory provides **centralized logging configuration** for the project.
It defines a standard way to:

* Create and store log files in the user’s home directory (`~/.fm_receiver/logs`).
* Configure console and file log outputs.
* Adjust log levels between `INFO` and `DEBUG`.
* Suppress excessive logs from noisy libraries (e.g., `matplotlib`).

##  Contents

* `__init__.py` – Makes this folder a package if needed.
* `logging_config.py` – Contains the `setup_logging` function to configure application logging.

##  Usage

Import and call `setup_logging()` at the entry point of your application:

```python
from logging_config import setup_logging

# Enable normal logging
setup_logging()

# Or enable debug-level logging
setup_logging(debug=True)
```

Once initialized:

* Logs will print to the **console** (`stdout`).
* Logs will also be written to a **file** at:

  ```
  ~/.fm_receiver/logs/fm_receiver.log
  ```


## Testing

To test logging setup, run:

```python
import logging
from logging_config import setup_logging

setup_logging(debug=True)
logger = logging.getLogger(__name__)

logger.info("This is an info message")
logger.debug("This is a debug message")
```

Expected behavior:

* Both messages appear in the console (since debug mode is enabled).
* Both messages are written to `~/.fm_receiver/logs/fm_receiver.log`.

---

