"""Sidebar component for the app."""

import reflex as rx
from ryoma_lab import styles
from ryoma_lab.components.chat_navbar import navbar
from ryoma_lab.states.base import BaseState

# Icons for the sidebar
ICONS = {
    "Workspace": "message-square-more",
    "Data Source": "database",
    "Document": "file-code",
    "Settings": "settings",
    "AI Assistant": "bot",
    "Vector Store": "package",
}


def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar_chat_history header component.
    """
    return rx.hstack(
        # The logo.
        rx.color_mode_cond(
            rx.image(src="/ryoma-horizontal-color.svg", height="3em"),
            rx.image(src="/ryoma-horizontal-white.svg", height="3em"),
        ),
        rx.spacer(),
        rx.cond(
            BaseState.sidebar_displayed,
            rx.link(
                rx.button(
                    rx.icon("github"),
                    color_scheme="gray",
                    variant="soft",
                    cursor="pointer",
                ),
                href="https://github.com/project-ryoma/ryoma",
                target="_blank",
            ),
        ),
        align="center",
        width="100%",
        border_bottom=styles.border,
        padding_x="1em",
        padding_y="2em",
    )


def sidebar_footer() -> rx.Component:
    """Sidebar footer.

    Returns:
        rx.Component: The sidebar_chat_history footer component.
    """
    return rx.hstack(
        rx.link(
            rx.center(
                rx.image(
                    src="/paneleft.svg",
                    height="2.5em",
                    padding="0.5em",
                    cursor="pointer",
                ),
                bg="transparent",
                border_radius=styles.border_radius,
                **styles.hover_accent_bg,
            ),
            on_click=BaseState.toggle_sidebar_displayed,
            transform=rx.cond(~BaseState.sidebar_displayed, "rotate(180deg)", ""),
            transition="transform 0.5s, left 0.5s",
            position="relative",
            left=rx.cond(BaseState.sidebar_displayed, "13.5em", "1em"),
            **styles.overlapping_button_style,
        ),
        rx.spacer(),
        width="100%",
        border_top=styles.border,
        padding="1em",
    )


def sidebar_item(text: str, url: str) -> rx.Component:
    """Sidebar item.

    Args:
        text: The text of the item.
        url: The URL of the item.

    Returns:
        rx.Component: The sidebar_chat_history item component.
    """
    # Whether the item is active.
    active = (rx.State.router.page.path == url.lower()) | (
        (rx.State.router.page.path == "/") & text == "Chat"
    )

    return rx.link(
        rx.hstack(
            rx.icon(ICONS[text], color="gray", size=24),
            rx.text(
                text,
                opacity=rx.cond(BaseState.sidebar_displayed, 1, 0),
                visibility=rx.cond(BaseState.sidebar_displayed, "visible", "hidden"),
                position=rx.cond(BaseState.sidebar_displayed, "relative", "absolute"),
                transition="opacity 0.3s, visibility 0.3s",
            ),
            bg=rx.cond(
                active,
                rx.color("accent", 2),
                "transparent",
            ),
            border=rx.cond(
                active,
                f"1px solid {rx.color('accent', 6)}",
                f"1px solid {rx.color('gray', 6)}",
            ),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            align="center",
            border_radius=styles.border_radius,
            width="100%",
            padding="1em",
        ),
        rx.cond(
            BaseState.sidebar_displayed,
            rx.cond(text == "Workspace" and active, navbar()),
        ),
        href=url,
        width="100%",
    )


def sidebar() -> rx.Component:
    """The sidebar_chat_history.

    Returns:
        The sidebar_chat_history component.
    """
    # Get all the decorated pages and add them to the sidebar_chat_history.
    from reflex.page import get_decorated_pages

    return rx.box(
        rx.vstack(
            sidebar_header(),
            rx.vstack(
                *[
                    sidebar_item(
                        text=page.get("title", page["route"].strip("/").capitalize()),
                        url=page["route"],
                    )
                    for page in get_decorated_pages()
                ],
                width="100%",
                overflow_y="auto",
                align_items="flex-start",
                padding="1em",
            ),
            rx.spacer(),
            sidebar_footer(),
            height="100dvh",
        ),
        display=["none", "none", "block"],
        max_width=styles.sidebar_width,
        width=rx.cond(BaseState.sidebar_displayed, "100%", "92px"),
        transition="width 0.5s",
        height="100%",
        position="sticky",
        top="0px",
        border_right=styles.border,
    )
