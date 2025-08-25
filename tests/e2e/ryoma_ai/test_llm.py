import pytest
from ryoma_ai.llm.provider import load_model_provider


def test_gp44all_model():
    """Test GPT4All model loading - will download model on first use."""
    model_id = "gpt4all:Llama-3.2-1B-Instruct-Q4_0.gguf"

    # Try to load the model
    gp44all_model = load_model_provider(model_id)

    if gp44all_model is None:
        pytest.skip(
            f"GPT4All model {model_id} not available. Model needs to be downloaded first."
        )

    # Test basic functionality
    response = gp44all_model.invoke("What is 2+2?")
    assert response is not None
    assert len(str(response)) > 0
    print(f"GPT4All response: {response}")
