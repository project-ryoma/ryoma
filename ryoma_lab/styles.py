"""Styles for the app."""

import reflex as rx

global_style = {
    ".gridjs-container": {
        "font_size": "12px",
    }
}
border_radius = "0.375rem"
border = f"1px solid {rx.color('gray', 6)}"
text_color = rx.color("gray", 11)
accent_text_color = rx.color("accent", 10)
accent_color = rx.color("accent", 1)
hover_accent_color = {"_hover": {"color": accent_text_color}}
hover_accent_bg = {"_hover": {"background_color": accent_color}}
content_width_vw = "90vw"
sidebar_width = "18em"

template_page_style = {
    "padding_top": "5em",
    "padding_x": ["auto", "0.5em"],
    "flex": "1",
    "overflow_x": "hidden",
}

template_content_style = {
    "border_radius": border_radius,
    "margin_bottom": "2em",
    "min_height": "90vh",
}

link_style = {
    "color": accent_text_color,
    "text_decoration": "none",
    **hover_accent_color,
}

overlapping_button_style = {
    "background_color": "white",
    "border_radius": border_radius,
}

markdown_style = {
    "h1": lambda text: rx.heading(text, size="5", margin_y="1em"),
    "h2": lambda text: rx.heading(text, size="3", margin_y="1em"),
    "h3": lambda text: rx.heading(text, size="1", margin_y="1em"),
    "p": lambda text: rx.text(text, color="black", margin_y="1em"),
    "code": lambda text: rx.code(text, color_scheme="gray"),
    "codeblock": lambda text, **props: rx.code_block(text, **props, margin_y="1em"),
    "a": lambda text, **props: rx.link(
        text,
        **props,
        color="blue",
        _hover={"color": "red"},
        font_weight="bold",
        text_decoration="underline",
        text_decoration_color=accent_text_color,
    ),
    "table": lambda el: rx.table.root(el, size="1", width="40em"),
    "thead": lambda el: rx.table.header(el, border_bottom=border),
    "tr": lambda text: rx.table.row(text, border_bottom=border),
}

# Common styles for questions and answers.
shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "20%"
message_style = dict(
    border_radius="5px",
    box_shadow=shadow,
    display="inline-block",
    margin_y="0.5em",
    padding_left="1em",
    padding_right="1em",
    max_width="44em",
)
