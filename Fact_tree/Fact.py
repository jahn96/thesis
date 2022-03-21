from __future__ import annotations

from typing import Union, List, TYPE_CHECKING
if TYPE_CHECKING:
    from Fact_tree.Node import Node


class Fact:
    def __init__(self, subj: Union[List[Union[Node, Fact]], Node, Fact, str] = None,
                 event: Node = None,
                 obj: Union[List[Union[Node, Fact]], Node, Fact, str] = None):
        self.__subj = subj
        self.__event = event
        self.__obj = obj

    @property
    def subj(self):
        return self.__subj

    @property
    def event(self):
        return self.__event

    @property
    def obj(self):
        return self.__obj

    @subj.setter
    def subj(self, subj):
        self.__subj = subj

    @event.setter
    def event(self, event):
        self.__event = event

    @obj.setter
    def obj(self, obj):
        self.__obj = obj
