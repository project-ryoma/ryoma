from typing import Optional, Any

import reflex as rx
from aita_lab.states.llm_providers import ChatModelProvider, EmbeddingModelProvider


def select_model(
        model_provider,
        model_value,
        on_model_value_change,
        style: Optional[dict] = None,
) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            placeholder="Select a model",
            style=style if style else {"width": "100%"},
        ),
        rx.select.content(
            *[
                rx.select.group(
                    rx.select.label(p.value.name),
                    rx.foreach(
                        p.value.models,
                        lambda x: rx.select.item(x, value=f"{p.value.id}:{x}"),
                    ),
                    width="100%",
                )
                for p in list(model_provider)
            ],
        ),
        value=model_value,
        on_change=on_model_value_change,
        default_value="gpt-3.5-turbo",
    )


def select_chat_model(
        model: str,
        set_model: Any,
        style: Optional[dict] = None,
) -> rx.Component:
    """The model selector."""
    return rx.form(
        rx.chakra.form_control(
            rx.text(
                "Chat Model *",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            select_model(
                ChatModelProvider, model, set_model, style
            ),
            label="Model",
            width="100%",
        ),
        width="100%",
    )


def select_embedding_model(model, set_model) -> rx.Component:
    """The model selector."""
    return rx.form(
        rx.chakra.form_control(
            rx.text(
                "Embedding Model *",
                asi_="div",
                mb="1",
                size="2",
                weight="bold",
            ),
            select_model(
                EmbeddingModelProvider, model, set_model
            ),
            label="Model",
            width="100%",
        ),
        width="100%",
    )
