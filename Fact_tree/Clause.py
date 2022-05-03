from typing import Union, List

from Fact_tree.Fact import Fact
from Fact_tree.Multiple import Multiple
from Fact_tree.Node import Node


class Clause(Fact):
    """
    Clause node in a fact tree
    """
    def __init__(self, connective: str, subj: Union[List[Union[Node, Fact]], Node, Fact, Multiple, str] = None,
                 event: Union[Node, Multiple] = None,
                 obj: Union[List[Union[Node, Fact]], Node, Fact, Multiple, str] = None):
        super().__init__(subj, event, obj)
        self.connective = connective

    def __repr__(self):
        return 'clause'
