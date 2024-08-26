import json
import random
from functools import reduce
from typing import Any, Dict, List, Optional

import reflex as rx
from reflex.state import MutableProxy, serialize_mutable_proxy

initial_nodes = [
    {
        "id": "1",
        "type": "input",
        "data": {
            "label": "__start__",
        },
        "position": {"x": 200, "y": 25},
    },
    {
        "id": "2",
        "data": {"label": "agent"},
        "position": {"x": 200, "y": 125},
    },
    {
        "id": "3",
        "type": "output",
        "data": {"label": "__end__"},
        "position": {"x": 200, "y": 250},
    },
]

initial_edges = [
    {"id": "e1-2", "source": "1", "target": "2", "label": "*", "animated": True},
    {"id": "e2-3", "source": "2", "target": "3", "label": "*", "animated": True},
]


def to_dict_if_proxy(obj):
    """Converts MutableProxy to dict if necessary"""
    if isinstance(obj, MutableProxy):
        json_obj = serialize_mutable_proxy(obj)
        return json.loads(json_obj)
    return obj


def handle_parent_expand(res: List[Any], update_item: Dict[str, Any]) -> None:
    for item in res:
        if item.get("id") == update_item.get("parentNode"):
            item["expanded"] = True
            break


def apply_changes(
    changes: List[Dict[str, Any]], elements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    # we need this hack to handle the setNodes and setEdges function of the useReactFlow hook for controlled flows
    if any(c["type"] == "reset" for c in changes):
        return [c["item"] for c in changes if c["type"] == "reset"]

    init_elements = [c["item"] for c in changes if c["type"] == "add"]
    return reduce(
        lambda res, item: apply_change(res, item, changes), elements, init_elements
    )


def apply_change(
    res: List[Dict[str, Any]], item: Dict[str, Any], changes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    current_changes = [c for c in changes if c["id"] == item["id"]]

    if not current_changes:
        res.append(item)
        return res

    update_item = item.copy()

    for current_change in current_changes:
        if current_change:
            if current_change["type"] == "select":
                update_item["selected"] = current_change["selected"]
            elif current_change["type"] == "position":
                if "position" in current_change:
                    update_item["position"] = current_change["position"]
                if "positionAbsolute" in current_change:
                    update_item["positionAbsolute"] = current_change["positionAbsolute"]
                if "dragging" in current_change:
                    update_item["dragging"] = current_change["dragging"]
                if update_item.get("expandParent"):
                    handle_parent_expand(res, update_item)
            elif current_change["type"] == "dimensions":
                if "dimensions" in current_change:
                    update_item["width"] = current_change["dimensions"]["width"]
                    update_item["height"] = current_change["dimensions"]["height"]
                if "updateStyle" in current_change:
                    update_item["style"] = {
                        **(update_item.get("style", {})),
                        **current_change["dimensions"],
                    }
                if "resizing" in current_change:
                    update_item["resizing"] = current_change["resizing"]
                if update_item.get("expandParent"):
                    handle_parent_expand(res, update_item)
            elif current_change["type"] == "remove":
                return res

    res.append(update_item)
    return res


class Graph(rx.Model):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class GraphState(rx.State):
    """The app state."""

    graph: Graph = Graph(nodes=initial_nodes, edges=initial_edges)

    current_tool: Optional[str]

    def add_tool_node(self, tool):
        self.current_tool = tool
        new_node_id = f"{len(self.graph.nodes) + 1}"
        node_type = "tool"
        x = random.randint(0, 500)
        y = random.randint(0, 500)

        new_node = {
            "id": new_node_id,
            "type": node_type,
            "data": {"label": self.current_tool},
            "position": {"x": x, "y": y},
            "draggable": True,
        }
        self.graph.nodes.append(new_node)

    def _set_graph(self, graph: Graph):
        self.graph = graph

    def add_random_node(self):
        new_node_id = f"{len(self.graph.nodes) + 1}"
        node_type = random.choice(["default"])
        # Label is random number
        label = new_node_id
        x = random.randint(0, 500)
        y = random.randint(0, 500)

        new_node = {
            "id": new_node_id,
            "type": node_type,
            "data": {"label": label},
            "position": {"x": x, "y": y},
            "draggable": True,
        }
        self.graph.nodes.append(new_node)

    def clear_graph(self):
        self.graph.nodes = initial_nodes
        self.graph.edges = initial_edges

    def on_connect(self, new_edge):
        # Iterate over the existing edges
        for i, edge in enumerate(self.graph.edges):
            # If we find an edge with the same ID as the new edge
            if edge["id"] == f"e{new_edge['source']}-{new_edge['target']}":
                # Delete the existing edge
                del self.graph.edges[i]
                break

        # Add the new edge
        self.graph.edges.append(
            {
                "id": f"e{new_edge['source']}-{new_edge['target']}",
                "source": new_edge["source"],
                "target": new_edge["target"],
                "label": random.choice(["+", "-", "*", "/"]),
                "animated": True,
            }
        )

    def on_nodes_change(self, changes):
        nodes = []
        for node in apply_changes(changes, self.graph.nodes):
            node = to_dict_if_proxy(node)
            nodes.append(node)
        self.graph.nodes = nodes
