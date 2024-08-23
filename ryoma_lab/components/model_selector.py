import reflex as rx

from ryoma_lab.states.llm_providers import ChatModelProvider, EmbeddingModelProvider


def select_model_render(
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
    return select_model_render(
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
    return select_model_render(
        ChatModelProvider,
        model_value,
        on_model_value_change,
        trigger_width,
    )
