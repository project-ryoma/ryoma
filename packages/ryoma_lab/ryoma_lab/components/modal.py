import reflex as rx
import reflex_chakra as rc
from ryoma_lab.states.workspace import ChatState, DataSourceState


def modal() -> rx.Component:
    """A modal to create a new workspace."""
    return rc.modal(
        rc.modal_overlay(
            rc.modal_content(
                rc.modal_header(
                    rc.hstack(
                        rc.text("Create new workspace"),
                        rc.icon(
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
                rc.modal_body(
                    rc.input(
                        placeholder="Type something...",
                        on_blur=ChatState.set_new_chat_name,
                        bg="#222",
                        border_color="#fff3",
                        _placeholder={"color": "#fffa"},
                    ),
                ),
                rc.modal_footer(
                    rc.button(
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
