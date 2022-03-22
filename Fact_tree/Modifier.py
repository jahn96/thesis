from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from typing import List, Dict, Union

from Attributes.Attribute import Attribute


class Modifier(Node):
    """
    Object modifier
    """
    def __init__(self, kind: str, attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, attrs)

    def __repr__(self):
        return 'modifier'
