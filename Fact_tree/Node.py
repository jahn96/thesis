from __future__ import annotations

from typing import List, Dict, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from Fact_tree.Fact import Fact

from Attributes.Attribute import Attribute
from Fact_tree.Base import Base


class Node(Base):
    def __init__(self, kind: str,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        """
        Node in a fact tree
        :param kind: literal value of a node
        :param attrs: attributes associated with this node
        :param kwargs: ??
        """
        super().__init__(kind, attrs)
        self.kind = kind
        self.attrs = attrs

    def get_attrs(self):
        return vars(self)
