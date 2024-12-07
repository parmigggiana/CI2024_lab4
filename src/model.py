"""
To perform the symbolic regression we need to define the model.
The function is represented as a tree structure, where each node is an operation or a variable.
"""

import copy
from enum import Enum
from typing import Self

import numpy as np


class NodeType(Enum):
    VARIABLE = 0
    CONSTANT = 1
    ADD = 2
    SUB = 3
    MUL = 4
    DIV = 5
    SIN = 6
    COS = 7
    EXP = 8
    ABS = 9
    LOG = 10


valid_children = {
    NodeType.VARIABLE: 0,
    NodeType.CONSTANT: 0,
    NodeType.ADD: 2,
    NodeType.SUB: 2,
    NodeType.MUL: 2,
    NodeType.DIV: 2,
    NodeType.SIN: 1,
    NodeType.COS: 1,
    NodeType.EXP: 1,
    NodeType.ABS: 1,
    NodeType.LOG: 1,
}

syms = {
    NodeType.ADD: "+",
    NodeType.SUB: "-",
    NodeType.MUL: "*",
    NodeType.DIV: "/",
    NodeType.SIN: "sin",
    NodeType.COS: "cos",
    NodeType.EXP: "exp",
    NodeType.ABS: "abs",
    NodeType.LOG: "log",
}


reverse_valid_children = {
    0: [NodeType.VARIABLE, NodeType.CONSTANT],
    1: [NodeType.SIN, NodeType.COS, NodeType.EXP, NodeType.ABS, NodeType.LOG],
    2: [NodeType.ADD, NodeType.SUB, NodeType.MUL, NodeType.DIV],
}


function_set = [
    NodeType.ADD,
    NodeType.SUB,
    NodeType.MUL,
    NodeType.DIV,
    NodeType.SIN,
    NodeType.COS,
    NodeType.EXP,
    NodeType.ABS,
    NodeType.LOG,
]

terminal_set = [
    NodeType.VARIABLE,
    NodeType.CONSTANT,
]


class Node:
    def __init__(self, type, value=None):
        self.type = type
        if type == NodeType.VARIABLE or type == NodeType.CONSTANT:
            assert value is not None, "Variable and constant nodes must have a value."
        self.value = value
        self.children = []
        self.parent = None
        self.depth = 1

    def f(self, x: np.ndarray):
        # Interpret the whole tree as function
        # Recursively evaluate the children
        match self.type:
            case NodeType.VARIABLE:
                return x[self.value]
            case NodeType.CONSTANT:
                return self.value
            case NodeType.ADD:
                return self.children[0].f(x) + self.children[1].f(x)
            case NodeType.SUB:
                return self.children[0].f(x) - self.children[1].f(x)
            case NodeType.MUL:
                return self.children[0].f(x) * self.children[1].f(x)
            case NodeType.DIV:
                return self.children[0].f(x) / self.children[1].f(x)
            case NodeType.SIN:
                return np.sin(self.children[0].f(x))
            case NodeType.COS:
                return np.cos(self.children[0].f(x))
            case NodeType.EXP:
                return np.exp(self.children[0].f(x))
            case NodeType.ABS:
                return np.abs(self.children[0].f(x))
            case NodeType.LOG:
                return np.log(self.children[0].f(x))

    def __str__(self):
        # Print the tree in a human-readable format
        # Recursively print the children
        first_child = self.children[0] if len(self.children) > 0 else "()"
        second_child = self.children[1] if len(self.children) > 1 else "()"

        match self.type:
            case NodeType.VARIABLE:
                return f"x[{self.value}]"
            case NodeType.CONSTANT:
                return f"{self.value:.3f}"
            case NodeType.ADD:
                return f"({first_child} + {second_child})"
            case NodeType.SUB:
                return f"({first_child} - {second_child})"
            case NodeType.MUL:
                return f"({first_child} * {second_child})"
            case NodeType.DIV:
                return f"({first_child} / {second_child})"
            case NodeType.SIN:
                return f"sin({first_child})"
            case NodeType.COS:
                return f"cos({first_child})"
            case NodeType.EXP:
                return f"exp({first_child})"
            case NodeType.ABS:
                return f"abs({first_child})"
            case NodeType.LOG:
                return f"log({first_child})"

    @property
    def flatten(self):
        return list(self)

    def __iter__(self):
        nodes = [
            self,
        ]
        while nodes:
            node = nodes.pop()
            nodes.extend(node.children)
            yield node

    def clone(self):
        return copy.deepcopy(self)

    def __contains__(self, item: Self):
        return item in self.flatten

    def append(self, child):
        self.children.append(child)
        child.parent = self
        child.depth = self.depth + 1

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, o: object) -> bool:
        return str(self) == str(o)

    def __repr__(self) -> str:
        return str(self)

    def simplify(self, x: np.ndarray):
        # Return a simplified version of the function f
        # resolving constant sub-trees

        simplified_root = self.clone()
        simplified_root.children = [
            child.simplify(x) for child in simplified_root.children
        ]

        # Simplify constant sub-trees
        if len(simplified_root.children) > 0 and all(
            child.type == NodeType.CONSTANT for child in simplified_root.children
        ):
            simplified_root = Node(NodeType.CONSTANT, value=simplified_root.f(x))

        # 1.24 - 1.24 OR x[0] - x[0]
        if (
            simplified_root.type == NodeType.SUB
            and all(
                x.type in [NodeType.CONSTANT, NodeType.VARIABLE]
                for x in simplified_root.children
            )
            and simplified_root.children[0].type == simplified_root.children[1].type
            and simplified_root.children[0].value == simplified_root.children[1].value
        ):
            simplified_root = Node(NodeType.CONSTANT, value=0)

        # x + 0 or 0 + x
        if simplified_root.type == NodeType.ADD:
            if (
                simplified_root.children[0].type == NodeType.CONSTANT
                and simplified_root.children[0].value == 0
            ):
                simplified_root.type = simplified_root.children[1].type
                simplified_root.value = simplified_root.children[1].value
                simplified_root.children = simplified_root.children[1].children
            elif (
                simplified_root.children[1].type == NodeType.CONSTANT
                and simplified_root.children[1].value == 0
            ):
                simplified_root.type = simplified_root.children[0].type
                simplified_root.value = simplified_root.children[0].value
                simplified_root.children = simplified_root.children[0].children

        # x * 1 or 1 * x
        if simplified_root.type == NodeType.MUL:
            if (
                simplified_root.children[0].type == NodeType.CONSTANT
                and simplified_root.children[0].value == 1
            ):
                simplified_root.type = simplified_root.children[1].type
                simplified_root.value = simplified_root.children[1].value
                simplified_root.children = simplified_root.children[1].children
            elif (
                simplified_root.children[1].type == NodeType.CONSTANT
                and simplified_root.children[1].value == 1
            ):
                simplified_root.type = simplified_root.children[0].type
                simplified_root.value = simplified_root.children[0].value
                simplified_root.children = simplified_root.children[0].children

        # x / 1
        if simplified_root.type == NodeType.DIV:
            if (
                simplified_root.children[1].type == NodeType.CONSTANT
                and simplified_root.children[1].value == 1
            ):
                simplified_root.type = simplified_root.children[0].type
                simplified_root.value = simplified_root.children[0].value
                simplified_root.children = simplified_root.children[0].children

        # 0 / x
        if simplified_root.type == NodeType.DIV:
            if (
                simplified_root.children[0].type == NodeType.CONSTANT
                and simplified_root.children[0].value == 0
            ):
                simplified_root = Node(NodeType.CONSTANT, value=0)

        # x * 0 or 0 * x
        if simplified_root.type == NodeType.MUL:
            if (
                simplified_root.children[0].type == NodeType.CONSTANT
                and simplified_root.children[0].value == 0
            ):
                simplified_root = Node(NodeType.CONSTANT, value=0)
            elif (
                simplified_root.children[1].type == NodeType.CONSTANT
                and simplified_root.children[1].value == 0
            ):
                simplified_root = Node(NodeType.CONSTANT, value=0)

        # Reset depths and parents
        nodes = [simplified_root]
        while nodes:
            node = nodes.pop()
            for child in node.children:
                child.depth = node.depth + 1
                child.parent = node
                nodes.append(child)

        return simplified_root

    def draw(self):
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(self)
        # Iterate over the nodes and create a list ordered by depth
        draw_nodes = np.empty(shape=(max([n.depth for n in self.flatten]),), dtype=list)
        for node in self.flatten:
            if draw_nodes[node.depth - 1] is None:
                draw_nodes[node.depth - 1] = []
            draw_nodes[node.depth - 1].append(node)

        # Draw the nodes
        coords = {}
        for i, nodes in enumerate(draw_nodes):
            for j, node in enumerate(nodes):
                x = (j + 0.5) / len(nodes)
                y = 0.98 - i / len(draw_nodes)
                if node.type == NodeType.VARIABLE:
                    text = f"x[{node.value}]"
                elif node.type == NodeType.CONSTANT:
                    text = f"{node.value:.2f}"
                else:
                    text = syms[node.type]

                ax.text(
                    x,
                    y,
                    text,
                    ha="center",
                    va="center",
                    bbox=dict(
                        facecolor="white",
                        alpha=1,
                        boxstyle="circle,pad=0.8",
                        lw=0.7,
                    ),
                    fontweight="bold",
                )
                coords[id(node)] = (x, y)

        # Draw the edges
        for node in self.flatten:
            if node.parent is not None:
                x0, y0 = coords[id(node.parent)]
                x1, y1 = coords[id(node)]
                ax.plot([x0, x1], [y0, y1], color="black")

        plt.show()
