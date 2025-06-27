# GNU Radio FM Receiver

A simple FM receiver built with [GNU Radio](https://www.gnuradio.org/) and the [gr-rds](https://github.com/bastibl/gr-rds) module to decode FM radio and RDS (Radio Data System) information.

## Requirements

Ensure the following dependencies are installed on your system:

- [GNU Radio](https://www.gnuradio.org/)
- [gr-rds](https://github.com/bastibl/gr-rds)
- Python 3.10
- `numpy`, `matplotlib` (automatically handled by `uv`)

## Running the Project

### Using [uv](https://docs.astral.sh/uv/getting-started/)

1. Install `uv` by following the [installation guide](https://docs.astral.sh/uv/getting-started/installation/).
2. Make sure GNU Radio and `gr-rds` are properly installed on your system.
3. Run the FM receiver:

```bash
uv run src/fm_receiver/main.py
```

Note: Ensure your virtual environment is created with system site packages enabled:

```bash
python3 -m venv .venv --system-site-packages
```
