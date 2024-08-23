from typing import Dict, Optional

import logging

from jupyter_ai_magics.utils import (
    AnyProvider,
    decompose_model_id,
    get_em_providers,
    get_lm_providers,
)


def get_model(
    model_id: str, model_type: Optional[str] = "chat", model_parameters: Optional[Dict] = None
) -> Optional[AnyProvider]:
    """
    Get a model instance from a model_id string. This is using the jupyter ai magic library to load the
    chat and embedding models dynamically.
    @param model_id: str: The model id string.
    @param model_type: model type can be either "chat" and "embedding".
    @param model_parameters: Optional[Dict]: Additional parameters to pass to the model.
    @return: Optional[AnyProvider]: The model instance.
    """
    providers = get_lm_providers() if model_type == "chat" else get_em_providers()
    provider_id, local_model_id = decompose_model_id(model_id, providers)

    print("provider_id", provider_id, local_model_id)

    if provider_id is None or provider_id not in providers:
        return None
    Provider = providers[provider_id]
    print(Provider)
    provider_params = {"model_id": local_model_id}
    model_parameters = model_parameters or {}
    return Provider(**provider_params, **model_parameters)
