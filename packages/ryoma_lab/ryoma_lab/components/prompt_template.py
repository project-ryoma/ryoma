"""The Prompt template Page."""

import reflex as rx
from ryoma_lab.components.code_editor import codeeditor
from ryoma_lab.states.prompt_template import PromptTemplate, PromptTemplateState
from ryoma_lab.templates import template


def prompt_card(pt: PromptTemplate):
    """Create a prompt card."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.chakra.card(
                rx.chakra.vstack(
                    rx.foreach(
                        pt.prompt_lines.split("\n"),
                        lambda line: rx.chakra.text(line, padding="2px"),
                    ),
                    align_items="flex-start",
                ),
                header=rx.chakra.heading(pt.prompt_template_name, size="md"),
                # adjust the size and make it scrollable
                direction="column",
                overflow="auto",
                height="300px",
                width="50%",
                margin_right="20px",
                cursor="pointer",
                _hover={"background_color": rx.color("gray", 2)},
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(pt.prompt_template_name, size="6"),
            rx.flex(
                rx.chakra.badge(f"Representation: {pt.prompt_repr}"),
                rx.chakra.badge(f"k_shot: {pt.k_shot}", color_scheme="purple"),
                rx.chakra.badge(f"Type: {pt.selector_type}", color_scheme="blue"),
                rx.chakra.badge(
                    f"Type: {pt.prompt_template_type}", color_scheme="green"
                ),
                justify="between",
                spacing="2",
                direction="row",
                padding="2px",
            ),
            rx.chakra.vstack(
                rx.foreach(pt.prompt_lines.split("\n"), lambda line: rx.text(line)),
                align_items="flex-start",
                font_size="sm",
                margin_top="10px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Close", size="2"),
                ),
                justify="end",
            ),
        ),
    )


def render_question():
    return rx.box(
        rx.chakra.text("A list of built-in prompt templates for you to choose from."),
        rx.badge(
            "Question: " + PromptTemplateState.question,
            variant="outline",
            margin_top="10px",
            size="3",
            padding="2px",
        ),
    )


def render_builtin_prompt_templates() -> rx.Component:
    return rx.flex(
        render_question(),
        rx.box(
            rx.chakra.flex(
                rx.foreach(
                    PromptTemplateState.prompt_templates,
                    lambda pt: rx.cond(
                        pt.prompt_template_type == "builtin",
                        prompt_card(pt),
                    ),
                )
            ),
            margin_top="20px",
            width="100%",
        ),
        direction="column",
        width="100%",
    )


def render_custom_prompt_templates() -> rx.Component:
    return rx.flex(
        rx.box(
            rx.chakra.text("A list of custom prompt templates that you have created."),
            margin_top="20px",
        ),
        rx.box(
            rx.chakra.flex(
                rx.foreach(
                    PromptTemplateState.prompt_templates,
                    lambda pt: rx.cond(
                        pt.prompt_template_type == "custom",
                        prompt_card(pt),
                    ),
                )
            ),
            margin_top="20px",
            width="100%",
        ),
        direction="column",
        width="100%",
    )


def render_create_prompt_template() -> rx.Component:
    return rx.flex(
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    "Create Prompt Template",
                    variant="solid",
                    on_click=PromptTemplateState.toggle_create_prompt_template_dialog,
                ),
            ),
            rx.dialog.content(
                rx.dialog.title("Create Prompt Template", size="6"),
                rx.dialog.description(
                    "Create a new prompt template.",
                    size="2",
                ),
                rx.flex(
                    rx.box(
                        rx.heading("Prompt Template Name", size="2"),
                        rx.input(
                            placeholder="Enter a Prompt Template Name",
                            on_blur=PromptTemplateState.set_prompt_template_name,
                        ),
                    ),
                    rx.box(
                        rx.heading("Copy An Existing Prompt Template", size="2"),
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Select a Prompt Template",
                                width="100%",
                            ),
                            rx.select.content(
                                rx.foreach(
                                    PromptTemplateState.prompt_templates,
                                    lambda pt: rx.select.item(
                                        pt.prompt_template_name,
                                        value=pt.prompt_template_name,
                                    ),
                                ),
                            ),
                            on_change=lambda x: PromptTemplateState.copy_to_current_prompt_template(
                                x
                            ),
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.heading("Prompt Representation", size="2"),
                        rx.select(
                            ["SQL", "Pandas"],
                            value=PromptTemplateState.prompt_repr,
                            on_change=PromptTemplateState.set_prompt_repr,
                            placeholder="Select a Prompt Representation",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.heading("K-shot", size="2"),
                        rx.input(
                            placeholder="Enter the K-shot value",
                            value=PromptTemplateState.k_shot,
                            on_change=PromptTemplateState.set_k_shot,
                            type="number",
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.heading("Example Format", size="2"),
                        rx.input(
                            placeholder="Enter the Example Format, e.g, {{context}}",
                            value=PromptTemplateState.example_format,
                            on_change=PromptTemplateState.set_example_format,
                        ),
                    ),
                    rx.box(
                        rx.heading("Template", size="2"),
                        codeeditor(
                            value=PromptTemplateState.prompt_template_lines,
                            width="100%",
                            min_height="20em",
                            extensions=rx.Var.create(
                                '[loadLanguage("sql"), loadLanguage("python")]',
                                _var_is_local=False,
                            ),
                            on_change=PromptTemplateState.set_prompt_template_lines,
                        ),
                    ),
                    direction="column",
                    spacing="4",
                    padding_y="2em",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Create", size="2"),
                        on_click=PromptTemplateState.create_prompt_template,
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            size="2",
                            variant="soft",
                            color_scheme="gray",
                            on_click=PromptTemplateState.toggle_create_prompt_template_dialog,
                        )
                    ),
                    spacing="3",
                    justify="end",
                ),
                on_escape_key_down=lambda _: PromptTemplateState.toggle_create_prompt_template_dialog(),
                on_interact_outside=lambda _: PromptTemplateState.toggle_create_prompt_template_dialog(),
            ),
            open=PromptTemplateState.create_prompt_template_dialog_open,
        ),
    )


def prompt_templatec_component() -> rx.Component:
    return rx.vstack(
        rx.heading("Builtin Prompt Templates", size="4"),
        rx.divider(),
        render_builtin_prompt_templates(),
        rx.divider(),
        rx.heading("Custom Prompt Templates", size="4"),
        render_create_prompt_template(),
        render_custom_prompt_templates(),
        width="100%",
    )
