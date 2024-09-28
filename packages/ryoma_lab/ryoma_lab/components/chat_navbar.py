import reflex as rx
from ryoma_lab.states.chat import ChatState


def chat_history_item(chat: str) -> rx.Component:
    """A sidebar_chat_history chat item.

    Args:
        chat: The chat item.
    """
    return rx.drawer.close(
        rx.hstack(
            rx.button(
                chat,
                on_click=lambda: ChatState.set_chat(chat),
                width="80%",
                variant="surface",
            ),
            rx.button(
                rx.icon(
                    tag="trash",
                    on_click=lambda: ChatState.delete_chat(chat),
                    stroke_width=1,
                ),
                width="20%",
                variant="surface",
                color_scheme="red",
            ),
            width="100%",
        )
    )


def sidebar_chat_history(trigger) -> rx.Component:
    """The sidebar_chat_history component."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.heading("Chat history", color=rx.color("mauve", 11)),
                    rx.divider(),
                    rx.foreach(
                        ChatState.chat_titles, lambda chat: chat_history_item(chat)
                    ),
                    align_items="stretch",
                    width="100%",
                ),
                top="auto",
                right="auto",
                height="100%",
                width="20em",
                padding="2em",
                background_color=rx.color("mauve", 2),
                outline="none",
            )
        ),
        direction="left",
    )


def create_chat_modal(trigger) -> rx.Component:
    """A modal to create a new chat."""
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.hstack(
                rx.input(
                    placeholder="Create a new chat with title...",
                    on_blur=ChatState.set_new_chat_title,
                    width=["15em", "20em", "30em", "30em", "30em", "30em"],
                ),
                rx.dialog.close(
                    rx.button(
                        "Create chat",
                        on_click=ChatState.create_chat,
                    ),
                ),
                background_color=rx.color("mauve", 1),
                spacing="2",
                width="100%",
            ),
        ),
    )


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                create_chat_modal(rx.button("+ New chat", variant="solid")),
                sidebar_chat_history(
                    rx.button(
                        rx.icon(
                            tag="messages-square",
                            color=rx.color("mauve", 10),
                        ),
                        rx.text("History"),
                        variant="soft",
                        color_scheme="gray",
                    )
                ),
                width="100%",
                justify="between",
            ),
            justify_content="space-between",
            align_items="center",
        ),
        backdrop_filter="auto",
        backdrop_blur="lg",
        padding="12px",
        border_bottom=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        position="sticky",
        top="0",
        z_index="100",
        align_items="center",
    )
