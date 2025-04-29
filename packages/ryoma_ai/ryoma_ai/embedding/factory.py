from ryoma_ai.embedding.client import EmbeddingClient, LangchainEmbeddingClient
from ryoma_ai.embedding.config import EmbeddingConfig
from ryoma_ai.llm.provider import load_model_provider


def create_embedder(config: EmbeddingConfig) -> EmbeddingClient:
    """
    Creates an EmbeddingClient using the provided configuration.
    """
    model_parameters = config.parameters or {}

    # Allow config.api_key and config.endpoint to override parameters
    if config.api_key:
        model_parameters["api_key"] = config.api_key
    if config.endpoint:
        model_parameters["endpoint"] = config.endpoint

    # Load LangChain-compatible embedding model
    langchain_embedder = load_model_provider(
        config.model,
        "embedding",
        model_parameters=model_parameters,
    )

    # Wrap it in Ryoma-compatible EmbeddingClient
    return LangchainEmbeddingClient(langchain_embedder)
