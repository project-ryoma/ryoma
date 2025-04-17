import logging

from langchain_core.embeddings import Embeddings
from ryoma_ai.llm.provider import load_model_provider


def get_embedding_client(
    selected_model: str, model_parameters: dict[str, str] = None
) -> Embeddings:
    logging.info(f"Creating embedding client for {selected_model}")
    return load_model_provider(
        selected_model,
        "embedding",
        model_parameters=model_parameters,
    )
