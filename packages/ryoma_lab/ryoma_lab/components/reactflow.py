from typing import Any, Dict, List

import reflex as rx


class ReactFlowLib(rx.Component):
    """A component that wraps a react flow lib."""

    library = "reactflow"

    def _get_custom_code(self) -> str:
        return """import 'reactflow/dist/style.css';
        """


class ReactFlow(ReactFlowLib):
    tag = "ReactFlow"

    nodes: rx.Var[List[Dict[str, Any]]]

    edges: rx.Var[List[Dict[str, Any]]]

    fit_view: rx.Var[bool]

    nodes_draggable: rx.Var[bool]

    nodes_connectable: rx.Var[bool]

    nodes_focusable: rx.Var[bool]

    on_nodes_change: rx.EventHandler[lambda e0: [e0]]

    on_edges_change: rx.EventHandler[lambda e0: [e0]]

    on_connect: rx.EventHandler[lambda e0: [e0]]

    def _get_custom_code(self) -> str:
        return """import 'reactflow/dist/style.css';
        """


class Background(ReactFlowLib):
    tag = "Background"

    color: rx.Var[str]

    gap: rx.Var[int]

    size: rx.Var[int]

    variant: rx.Var[str]


class Controls(ReactFlowLib):
    tag = "Controls"


class ApplyNodeChanges(ReactFlowLib):
    tag = "applyNodeChanges"


react_flow = ReactFlow.create
background = Background.create
controls = Controls.create
apply_node_changes = ApplyNodeChanges.create
