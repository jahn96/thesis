from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from typing import List, Dict, Union

from Attributes.Attribute import Attribute


class Event(Node):
    def __init__(self, kind: str, passive: bool = False, neg: bool = False,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, neg, attrs)
        self.passive = passive

    def __repr__(self):
        return 'event'
