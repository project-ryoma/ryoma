from typing import Optional

import reflex as rx
from langchain_core.embeddings import Embeddings as LangchainEmbeddings


class Embedding(rx.Base):
    name: str
    model: Optional[LangchainEmbeddings]
