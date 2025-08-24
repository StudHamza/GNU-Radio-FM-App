
# `core/` Directory Documentation

## Purpose
Provides a central way to manage application configuration.  
The `ConfigManager` class handles:
- Loading configuration from a JSON file.
- Saving updated configuration back to disk.
- Falling back to a default configuration if none exists or is invalid.
- Guaranteeing that a `config/` directory and `config.json` file exist.

## Contents
- `config_manager.py` – Contains the `ConfigManager` class for handling JSON-based configuration.

## Usage

```python
from config_manager import ConfigManager

# Initialize (loads existing config or creates default)
config = ConfigManager()

# Access config values
stations = config.get("stations")
volume = config.get("volume", 5)

# Update config
config.set("volume", 10)

# Save changes
config.save()
````

By default, the configuration is stored in:

```
<current working directory>/config/config.json
```

## 🛠️ Development Notes

* If `config.json` is missing or invalid, a default configuration is created:

  ```json
  {
    "stations": [88700000.0],
    "volume": 0,
    "outdir": null
  }
  ```
* If `"stations"` is missing or empty, it falls back to the default list.
* Errors during load/save are logged but do not stop execution.
* Logs are sent through the application logger (`logging`).

## Testing

Example test:

```python
from config_manager import ConfigManager

config = ConfigManager()

print(config.get("stations"))  # Should show [88700000.0] by default
config.set("volume", 7)
config.save()
```

Expected:

* Console log shows `Configuration saved to <path>/config/config.json`.
* `config.json` contains the updated volume value.

## References

* Python `json` module docs: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)
* Python `logging` module docs: [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)
* Python `pathlib` module docs: [https://docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html)

