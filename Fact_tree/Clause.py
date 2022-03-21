from typing import Union, List

from Fact_tree.Fact import Fact
from Fact_tree.Node import Node


class Clause(Fact):
    def __init__(self, subj: Union[List[Union[Node, Fact]], Node, Fact, str] = None,
                 event: Node = None,
                 obj: Union[List[Union[Node, Fact]], Node, Fact, str] = None):
        super().__init__(subj, event, obj)

    def __repr__(self):
        return 'clause'
