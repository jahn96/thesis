from typing import Dict, Union, List

from Attributes.Attribute import Attribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Node import Node


# TODO: think about factoring out the attrs to key args
class Phrase(Event):
    def __init__(self, kind: str, passive: bool = False, neg: bool = False,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, passive, neg, attrs)

    def __repr__(self):
        return 'phrase'
