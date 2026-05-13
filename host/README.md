# EchoGlove host

Python 3.12 (managed by [uv](https://github.com/astral-sh/uv)) host-side package: reads sensor data from the glove over USB serial (later BLE), runs fusion, and renders the live hand pose.

## Setup

```bash
brew install uv      # one-time
cd host
uv sync              # installs deps + creates .venv
```

## Common commands

```bash
uv run pytest tests/ -v                  # run tests
uv run python -m echoglove.serial_reader # run the serial reader (once it exists)
uv run ruff check .                      # lint
```

## Layout

- `src/echoglove/` — package code (serial reader, fusion, viewer)
- `tests/` — pytest suite

The project uses uv's default `src/` layout. `uv run` installs the project editably in the venv, so `import echoglove.<module>` works from tests without `PYTHONPATH` tweaks.
