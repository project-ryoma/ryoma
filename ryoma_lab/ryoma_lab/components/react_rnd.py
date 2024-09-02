from typing import Any, Dict, Optional

import reflex as rx


class DraggableData(rx.Base):
    x: int
    y: int
    deltaX: int
    deltaY: int
    lastX: int
    lastY: int


class RnD(rx.Component):
    library = "react-rnd"
    tag = "Rnd"

    # Props
    default: rx.Var[Dict[str, Any]]
    position: rx.Var[Dict[str, int]]
    size: rx.Var[Dict[str, int]]
    bounds: rx.Var[str]
    min_width: rx.Var[int]
    min_height: rx.Var[int]
    max_width: rx.Var[int]
    max_height: rx.Var[int]
    drag_grid: rx.Var[tuple[int, int]]
    resize_grid: rx.Var[tuple[int, int]]
    lockAspectRatio: rx.Var[bool]
    enable_user_select_hack: rx.Var[bool]
    disable_dragging: rx.Var[bool]
    enable: rx.Var[Dict[str, bool]]

    # Event handlers
    on_drag_start: rx.Var[Optional[rx.EventHandler]]
    on_drag: rx.Var[Optional[rx.EventHandler]]
    on_drag_stop: rx.Var[Optional[rx.EventHandler]]
    on_resize_start: rx.Var[Optional[rx.EventHandler]]
    on_resize: rx.Var[Optional[rx.EventHandler]]
    on_resize_stop: rx.Var[Optional[rx.EventHandler]]

    def get_event_triggers(self) -> Dict[str, Any]:
        """Get event triggers."""

        def drag_signature(e0, data: DraggableData):
            """Get the drag signature."""
            return [
                data.x,
                data.y,
                data.deltaX,
                data.deltaY,
                data.lastX,
                data.lastY,
            ]

        def resize_signature(e0, direction, ref, delta, position):
            """Get the resize signature."""
            return [
                direction,
                delta.width,
                delta.height,
                position.x,
                position.y,
            ]

        return {
            **super().get_event_triggers(),
            "on_drag_start": drag_signature,
            "on_drag": drag_signature,
            "on_drag_stop": drag_signature,
            "on_resize_start": resize_signature,
            "on_resize": resize_signature,
            "on_resize_stop": resize_signature,
        }


rnd = RnD.create
