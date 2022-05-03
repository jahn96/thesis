from __future__ import annotations
from typing import List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from Fact_tree.Node import Node
    from Fact_tree.Clause import Clause
    from Fact_tree.Fact import Fact


class Multiple:
    def __init__(self, conj: str, nodes: List[Union[Node, Clause, Fact]], attrs: dict = None):
        self.conj = conj
        self.nodes = nodes
        self.attrs = attrs

    def __repr__(self):
        return 'multiple_' + str(self.nodes[0])
