import reflex as rx

from ryoma_lab.components.model_selector import embedding_model_selector
from ryoma_lab.states.embedding import EmbeddingState


def model_config_render() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("API Key"),
            rx.input(
                value=EmbeddingState.api_key,
                on_change=EmbeddingState.set_api_key,
            ),
        ),
        rx.hstack(
            rx.text("Dimension"),
            rx.input(
                value=EmbeddingState.dimension,
                on_change=EmbeddingState.set_dimension,
            ),
        ),
        width="100%",
        spacing="4",
    )


def embedding_component() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Model", width="100px"),
            embedding_model_selector(
                EmbeddingState.selected_model,
                EmbeddingState.set_model,
            ),
        ),
        rx.hstack(
            rx.text("API Key", width="100px"),
            rx.input(
                value=EmbeddingState.api_key,
                on_change=EmbeddingState.set_api_key,
            ),
        ),
        rx.hstack(
            rx.text("Dimension", width="100px"),
            rx.input(
                value=EmbeddingState.dimension,
                on_change=EmbeddingState.set_dimension,
            ),
        ),
        width="100%",
        padding_x="2em",
    )
