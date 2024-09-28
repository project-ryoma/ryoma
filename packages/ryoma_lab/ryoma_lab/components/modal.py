import reflex as rx
from ryoma_lab.states.workspace import ChatState, DataSourceState


def modal() -> rx.Component:
    """A modal to create a new workspace."""
    return rx.chakra.modal(
        rx.chakra.modal_overlay(
            rx.chakra.modal_content(
                rx.chakra.modal_header(
                    rx.chakra.hstack(
                        rx.chakra.text("Create new workspace"),
                        rx.chakra.icon(
                            tag="close",
                            font_size="sm",
                            on_click=ChatState.toggle_modal,
                            color="#fff8",
                            _hover={"color": "#fff"},
                            cursor="pointer",
                        ),
                        align_items="center",
                        justify_content="space-between",
                    )
                ),
                rx.chakra.modal_body(
                    rx.chakra.input(
                        placeholder="Type something...",
                        on_blur=ChatState.set_new_chat_name,
                        bg="#222",
                        border_color="#fff3",
                        _placeholder={"color": "#fffa"},
                    ),
                ),
                rx.chakra.modal_footer(
                    rx.chakra.button(
                        "Create",
                        bg="#5535d4",
                        box_shadow="md",
                        px="4",
                        py="2",
                        h="auto",
                        _hover={"bg": "#4c2db3"},
                        on_click=ChatState.create_chat,
                    ),
                ),
                bg="#222",
                color="#fff",
            ),
        ),
        is_open=ChatState.modal_open,
    )
