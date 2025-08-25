#!/usr/bin/env python3
"""
Helper script to download GPT4All models for testing.

Usage:
    python download_gpt4all_model.py [model_name]

If no model_name is provided, downloads the default test model.
"""
import sys
from pathlib import Path


def download_model(model_name="Llama-3.2-1B-Instruct-Q4_0.gguf"):
    """Download a GPT4All model."""
    try:
        from gpt4all import GPT4All

        print(f"Downloading GPT4All model: {model_name}")
        print("This may take a few minutes depending on your internet connection...")

        # Check if model already exists
        cache_dir = Path.home() / ".cache" / "gpt4all"
        model_path = cache_dir / model_name

        if model_path.exists():
            print(f"Model {model_name} already exists at {model_path}")
            return True

        # Create GPT4All instance - this will trigger download
        model = GPT4All(model_name)

        print(f"Model {model_name} downloaded successfully!")
        print(f"Model path: {model_path}")

        # Test the model
        print("Testing model...")
        response = model.generate("Hello, how are you?", max_tokens=50)
        print(f"Test response: {response}")

        return True

    except ImportError:
        print("GPT4All not available. Please install with: pip install gpt4all")
        return False
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False


if __name__ == "__main__":
    model_name = sys.argv[1] if len(sys.argv) > 1 else "Llama-3.2-1B-Instruct-Q4_0.gguf"
    success = download_model(model_name)
    sys.exit(0 if success else 1)
