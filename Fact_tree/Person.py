from typing import List, Dict, Union

from Attributes.Attribute import Attribute
from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from Fact_tree.Object import Object


class Person(Object):
    """
    Person node in a fact tree
    """
    def __init__(self, kind: str, neg: bool = False,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, neg, attrs)

    def __repr__(self):
        return 'person'
