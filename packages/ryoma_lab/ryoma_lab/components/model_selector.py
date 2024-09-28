import reflex as rx
from ryoma_lab.models.llm import ChatModelProvider, EmbeddingModelProvider


def model_selector(
    model_provider,
    model_value,
    on_model_value_change,
    trigger_width: str = "12em",
) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            placeholder="Select a model",
            width=trigger_width,
        ),
        rx.select.content(
            *[
                rx.select.group(
                    rx.select.label(p.value.name),
                    rx.foreach(
                        p.value.models,
                        lambda x: rx.select.item(x, value=f"{p.value.id}:{x}"),
                    ),
                )
                for p in list(model_provider)
            ],
        ),
        value=model_value,
        on_change=on_model_value_change,
        default_value="gpt-3.5-turbo",
    )


def embedding_model_selector(
    model_value,
    on_model_value_change,
    trigger_width: str = "12em",
) -> rx.Component:
    """
    Embedding model selector.
    @param model_value: model value selected.
    @param on_model_value_change: on model value change.
    @param trigger_width: change trigger width.
    @return: Embedding model selector component.
    """
    return model_selector(
        EmbeddingModelProvider,
        model_value,
        on_model_value_change,
        trigger_width,
    )


def chat_model_selector(
    model_value,
    on_model_value_change,
    trigger_width: str = "12em",
) -> rx.Component:
    """
    Chat model selector.
    @param model_value: model value selected.
    @param on_model_value_change: On model value change.
    @param trigger_width: change trigger width.
    @return: the chat model selector component.
    """
    return model_selector(
        ChatModelProvider,
        model_value,
        on_model_value_change,
        trigger_width,
    )
