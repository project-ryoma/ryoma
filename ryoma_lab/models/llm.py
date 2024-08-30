from enum import Enum

from jupyter_ai_magics.embedding_providers import (
    GPT4AllEmbeddingsProvider,
    HfHubEmbeddingsProvider,
)
from jupyter_ai_magics.providers import (
    AI21Provider,
    GPT4AllProvider,
    HfHubProvider,
    QianfanProvider,
    TogetherAIProvider,
)


class BedrockProvider:
    id = "bedrock"
    name = "Amazon Bedrock"
    models = [
        "amazon.titan-text-express-v1",
        "amazon.titan-text-lite-v1",
        "ai21.j2-ultra-v1",
        "ai21.j2-mid-v1",
        "cohere.command-light-text-v14",
        "cohere.command-text-v14",
        "cohere.command-r-v1:0",
        "cohere.command-r-plus-v1:0",
        "meta.llama2-13b-chat-v1",
        "meta.llama2-70b-chat-v1",
        "meta.llama3-8b-instruct-v1:0",
        "meta.llama3-70b-instruct-v1:0",
        "meta.llama3-1-8b-instruct-v1:0",
        "meta.llama3-1-70b-instruct-v1:0",
        "mistral.mistral-7b-instruct-v0:2",
        "mistral.mixtral-8x7b-instruct-v0:1",
        "mistral.mistral-large-2402-v1:0",
    ]


class BedrockChatProvider:
    id = "bedrock-chat"
    name = "Amazon Bedrock Chat"
    models = [
        "amazon.titan-text-express-v1",
        "amazon.titan-text-lite-v1",
        "anthropic.claude-v2",
        "anthropic.claude-v2:1",
        "anthropic.claude-instant-v1",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "meta.llama2-13b-chat-v1",
        "meta.llama2-70b-chat-v1",
        "meta.llama3-8b-instruct-v1:0",
        "meta.llama3-70b-instruct-v1:0",
        "meta.llama3-1-8b-instruct-v1:0",
        "meta.llama3-1-70b-instruct-v1:0",
        "mistral.mistral-7b-instruct-v0:2",
        "mistral.mixtral-8x7b-instruct-v0:1",
        "mistral.mistral-large-2402-v1:0",
    ]


class SmEndpointProvider:
    id = "sagemaker-endpoint"
    name = "SageMaker endpoint"
    models = ["*"]


class BedrockEmbeddingsProvider:
    id = "bedrock"
    name = "Bedrock"
    models = [
        "amazon.titan-embed-text-v1",
        "amazon.titan-embed-text-v2:0",
        "cohere.embed-english-v3",
        "cohere.embed-multilingual-v3",
    ]


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
        "chat_llama2_70b",
        "chat_nemotron_steerlm_8b",
        "chat_mistral_7b",
        "chat_nv_llama2_rlhf_70b",
        "chat_llama2_13b",
        "chat_steerlm_llama_70b",
        "chat_llama2_code_13b",
        "chat_yi_34b",
        "chat_mixtral_8x7b",
        "chat_neva_22b",
        "chat_llama2_code_34b",
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
    id = "anthropic"
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
