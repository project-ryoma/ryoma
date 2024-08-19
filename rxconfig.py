import logging

import reflex as rx
from reflex.constants import LogLevel

config = rx.Config(
    app_name="ryoma_lab",
    loglevel=LogLevel.INFO,
)

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
