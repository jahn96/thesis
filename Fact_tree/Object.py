from typing import List

from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from typing import List, Dict, Union

from Attributes.Attribute import Attribute


class Object(Node):
    def __init__(self, kind: str, neg: bool = False,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, neg, attrs)

    def __repr__(self):
        return 'object'
