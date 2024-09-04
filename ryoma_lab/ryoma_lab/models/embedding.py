from typing import Optional

import reflex as rx


class Embedding(rx.Base):
    model: str
    model_parameters: Optional[dict[str, Optional[str]]] = None
