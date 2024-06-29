from enum import Enum

# get embedding models
from jupyter_ai_magics.embedding_providers import (
    BedrockEmbeddingsProvider,
    GPT4AllEmbeddingsProvider,
    HfHubEmbeddingsProvider,
)
from jupyter_ai_magics.providers import (
    AI21Provider,
    BedrockChatProvider,
    BedrockProvider,
    GPT4AllProvider,
    HfHubProvider,
    QianfanProvider,
    SmEndpointProvider,
    TogetherAIProvider,
)


class OpenAIEmbeddingsProvider:
    id = "openai"
    name = "OpenAI"
    models = [
        "text-embedding-ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large",
    ]


class MistralAIEmbeddingsProvider:
    id = "mistralai"
    name = "MistralAI"
    models = [
        "mistral-embed",
    ]


class CohereEmbeddingsProvider:
    id = "cohere"
    name = "Cohere"
    models = [
        "embed-english-v2.0",
        "embed-english-light-v2.0",
        "embed-multilingual-v2.0",
        "embed-english-v3.0",
        "embed-english-light-v3.0",
        "embed-multilingual-v3.0",
        "embed-multilingual-light-v3.0",
    ]


class OpenAIProvider:
    name = "OpenAI"
    id = "openai"
    models = ["babbage-002", "davinci-002", "gpt-3.5-turbo-instruct"]


class ChatOpenAIProvider:
    name = "OpenAIChat"
    id = "openai-chat"
    models = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-0301",  # Deprecated as of 2024-06-13
        "gpt-3.5-turbo-0613",  # Deprecated as of 2024-06-13
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",  # Deprecated as of 2024-06-13
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0613",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
    ]


class AzureChatOpenAIProvider:
    id = "azure-chat-openai"
    name = "Azure OpenAI"
    models = ["*"]


class ChatNVIDIAProvider:
    id = "nvidia-chat"
    name = "NVIDIA"
    models = [
        "playground_llama2_70b",
        "playground_nemotron_steerlm_8b",
        "playground_mistral_7b",
        "playground_nv_llama2_rlhf_70b",
        "playground_llama2_13b",
        "playground_steerlm_llama_70b",
        "playground_llama2_code_13b",
        "playground_yi_34b",
        "playground_mixtral_8x7b",
        "playground_neva_22b",
        "playground_llama2_code_34b",
    ]


class GeminiProvider:
    id = "gemini"
    name = "Gemini"
    models = [
        "gemini-1.0-pro",
        "gemini-1.0-pro-001",
        "gemini-1.0-pro-latest",
        "gemini-1.0-pro-vision-latest",
        "gemini-pro",
        "gemini-pro-vision",
    ]


class AnthropicProvider:
    id = "anthropic"
    name = "Anthropic"
    models = [
        "claude-v1",
        "claude-v1.0",
        "claude-v1.2",
        "claude-2",
        "claude-2.0",
        "claude-instant-v1",
        "claude-instant-v1.0",
        "claude-instant-v1.2",
    ]


class ChatAnthropicProvider:
    id = "anthropic-chat"
    name = "ChatAnthropic"
    models = [
        "claude-2.0",
        "claude-2.1",
        "claude-instant-1.2",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]


class CohereProvider:
    id = "cohere"
    name = "Cohere"
    models = [
        "command",
        "command-nightly",
        "command-light",
        "command-light-nightly",
        "command-r-plus",
        "command-r",
    ]


class ChatModelProvider(Enum):
    openai_chat = ChatOpenAIProvider
    openai = OpenAIProvider
    ai21 = AI21Provider
    amazon_bedrock = BedrockProvider
    amazon_bedrock_chat = BedrockChatProvider
    anthropic = AnthropicProvider
    anthropic_chat = ChatAnthropicProvider
    azure_chat_openai = AzureChatOpenAIProvider
    cohere = CohereProvider
    gemini = GeminiProvider
    gpt4all = GPT4AllProvider
    huggingface_hub = HfHubProvider
    nvidia_chat = ChatNVIDIAProvider
    qianfan = QianfanProvider
    sagemaker_endpoint = SmEndpointProvider
    together_ai = TogetherAIProvider


class EmbeddingModelProvider(Enum):
    bedrock = BedrockEmbeddingsProvider
    cohere = CohereEmbeddingsProvider
    gpt4all = GPT4AllEmbeddingsProvider
    openai = OpenAIEmbeddingsProvider
    mistralai = MistralAIEmbeddingsProvider
    huggingface_hub = HfHubEmbeddingsProvider
