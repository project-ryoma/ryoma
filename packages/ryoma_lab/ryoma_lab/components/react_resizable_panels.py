"""Reflex custom component ResizablePanels."""

# For wrapping react guide, visit https://reflex.dev/docs/wrapping-react/overview/

from types import SimpleNamespace
from typing import Any, Literal

import reflex as rx

LiteralDirection = Literal["horizontal", "vertical"]

lib_name = "react-resizable-panels@^2.0.19"


class ResizablePanels(rx.Component):
    """ResizablePanels component."""

    # The React library to wrap.
    library = lib_name


class PanelRoot(rx.el.Div):
    def add_style(self) -> dict[str, Any] | None:
        return {"width": "100%", "height": "100%"}


class PanelGroup(ResizablePanels):
    tag = "PanelGroup"

    alias = "ResizablePanelGroup"

    # Unique id to auto-save the group layout via localStorage
    auto_save_id: rx.Var[str]

    # Group orientation
    direction: rx.Var[LiteralDirection]

    on_layout: rx.EventHandler[lambda e0: [e0]]

    # not sure how to make this one works
    # storage: rx.Var[Any]


class Panel(ResizablePanels):
    tag = "Panel"

    alias = "ResizablePanel"

    # Whether the panel is collapsible
    collapsible: rx.Var[bool]

    # Panel should collapse to this size
    collapsed_size: rx.Var[int]

    # Default size of the panel (should be a number between 1 - 100)
    default_size: rx.Var[int]

    # Maximum size of the panel (should be a number between 1 - 100)
    max_size: rx.Var[int]

    # Minimum size of the panel (should be a number between 1 - 100)
    min_size: rx.Var[int]

    # Event handlers triggered when the panel is collapsed
    on_collapse: rx.EventHandler[lambda: []]

    # Event handlers triggered when the panel is expanded
    on_expand: rx.EventHandler[lambda: []]

    # Event handlers triggered when the panel is resized
    on_resize: rx.EventHandler[lambda e0: [e0]]

    # Order of the panel within the group
    order: rx.Var[int]


class PanelResizeHandle(ResizablePanels):
    tag = "PanelResizeHandle"

    alias = "ResizablePanelResizeHandle"

    def add_style(self) -> dict[str, Any] | None:
        return {
            "width": "7px",
            "background": rx.color("accent", 7),
            "opacity": 0.0,
            "_hover": {"opacity": 1.0},
        }


class ResizablePanelsNamespace(SimpleNamespace):
    group = staticmethod(PanelGroup.create)
    panel = staticmethod(Panel.create)
    handle = staticmethod(PanelResizeHandle.create)


resizable_panels = ResizablePanelsNamespace()
