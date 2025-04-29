# Ryoma Lab

Welcome to Ryoma Lab! Ryoma lab is an interactive platform where you can ask questions, run code, and explore data using Ryoma AI.

## How to get started?
1. Before you start, make sure you have ryoma installed by running the following command:
```text
pip install ryoma
```
2. Once installed, you can setup configuration file `rxconfig.py` in your project:
```python
import reflex as rx
from reflex.constants import LogLevel

config = rx.Config(
    app_name="ryoma_lab",
    loglevel=LogLevel.INFO,
)
```
more information on configuration can be found [Reflex config](https://reflex.dev/docs/getting-started/configuration/).

3. Now you can run the following command to start Ryoma Lab:
```bash
ryoma_lab run
```

The app will start running on `http://localhost:3000/`. You can open this URL in your browser to start using Ryoma Lab.

## Components

