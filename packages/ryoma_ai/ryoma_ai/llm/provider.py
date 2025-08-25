import logging
from typing import Any, Dict, Optional, Union

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel


def load_model_provider(
    model_id: str,
    model_type: Optional[str] = "chat",
    model_parameters: Optional[Dict] = None,
) -> Optional[Union[BaseChatModel, Embeddings]]:
    """
    Get a model instance from a model_id string using langchain providers natively.
    @param model_id: str: The model id string in format 'provider:model_name' or just 'model_name' for OpenAI.
    @param model_type: model type can be either "chat" and "embedding".
    @param model_parameters: Optional[Dict]: Additional parameters to pass to the model.
    @return: Optional[Union[BaseChatModel, Embeddings]]: The model instance.
    """
    logging.info(
        f"Loading model provider with model id: {model_id}, model type: {model_type}"
    )

    model_parameters = model_parameters or {}

    # Parse provider and model name
    if ":" in model_id:
        provider_id, model_name = model_id.split(":", 1)
    else:
        # Default to OpenAI if no provider specified
        provider_id = "openai"
        model_name = model_id

    try:
        if model_type == "chat":
            return _load_chat_model(provider_id, model_name, model_parameters)
        elif model_type == "embedding":
            return _load_embedding_model(provider_id, model_name, model_parameters)
        else:
            logging.error(f"Unsupported model type: {model_type}")
            return None
    except Exception as e:
        logging.error(f"Failed to load model {model_id}: {str(e)}")
        return None


def _load_chat_model(provider_id: str, model_name: str, model_parameters: Dict) -> Any:
    """Load a chat model based on the provider."""
    logging.info(
        f"Loading chat model with provider: {provider_id}, model: {model_name}, parameters: {model_parameters}"
    )
    if provider_id in ["openai", "openai-chat"]:
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_openai not available. Install with: pip install langchain-openai"
            )
            return None

    elif provider_id == "gpt4all":
        try:
            from langchain_community.llms import GPT4All

            # Use GPT4All LLM directly - it already works with the ryoma agent system
            # Enable auto-download of models if they don't exist locally
            model_parameters.setdefault("allow_download", True)
            return GPT4All(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "GPT4All dependencies not available. Install with: pip install gpt4all"
            )
            return None
        except Exception as e:
            if "Model file does not exist" in str(e):
                logging.error(
                    f"GPT4All model '{model_name}' not found locally. "
                    f"The model will be downloaded on first use, but this may take time. "
                    f"Error: {e}"
                )
            else:
                logging.error(f"Failed to load GPT4All model '{model_name}': {e}")
            return None

    elif provider_id == "huggingface":
        try:
            from langchain_huggingface import ChatHuggingFace

            return ChatHuggingFace(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_huggingface not available. Install with: pip install langchain-huggingface"
            )
            return None

    elif provider_id == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_anthropic not available. Install with: pip install langchain-anthropic"
            )
            return None

    elif provider_id == "azure-chat-openai":
        try:
            from langchain_openai import AzureChatOpenAI

            return AzureChatOpenAI(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_openai not available. Install with: pip install langchain-openai"
            )
            return None

    elif provider_id in ["google", "gemini", "google-genai"]:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_google_genai not available. Install with: pip install langchain-google-genai"
            )
            return None
        except Exception as e:
            logging.error(
                f"Failed to initialize Google Gemini model. Make sure GOOGLE_API_KEY is set. Error: {e}"
            )
            return None

    elif provider_id == "google-vertexai":
        try:
            from langchain_google_vertexai import ChatVertexAI

            return ChatVertexAI(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_google_vertexai not available. Install with: pip install langchain-google-vertexai"
            )
            return None
        except Exception as e:
            logging.error(
                f"Failed to initialize Google Vertex AI model. Check authentication. Error: {e}"
            )
            return None

    else:
        logging.error(f"Unsupported chat provider: {provider_id}")
        return None


def _load_embedding_model(
    provider_id: str, model_name: str, model_parameters: Dict
) -> Optional[Embeddings]:
    """Load an embedding model based on the provider."""
    if provider_id in ["openai", "openai-embedding"]:
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_openai not available. Install with: pip install langchain-openai"
            )
            return None

    elif provider_id == "huggingface":
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name=model_name, **model_parameters)
        except ImportError:
            logging.error(
                "langchain_huggingface not available. Install with: pip install langchain-huggingface"
            )
            return None

    else:
        logging.error(f"Unsupported embedding provider: {provider_id}")
        return None
