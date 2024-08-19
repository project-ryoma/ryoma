from jupyter_ai_magics.providers import *
from jupyter_ai_magics.utils import decompose_model_id, get_lm_providers
from langchain_core.runnables import RunnableSerializable


def get_model(model_id: str, model_parameters: Optional[Dict]) -> Optional[RunnableSerializable]:
    providers = get_lm_providers()
    provider_id, local_model_id = decompose_model_id(model_id, providers)
    if provider_id is None or provider_id not in providers:
        return None
    Provider = providers[provider_id]
    provider_params = {"model_id": local_model_id}
    model_parameters = model_parameters or {}
    return Provider(**provider_params, **model_parameters)
