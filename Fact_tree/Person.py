from typing import List, Dict, Union

from Attributes.Attribute import Attribute
from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from Fact_tree.Object import Object


class Person(Object):
    def __init__(self, kind: str, neg: bool = False,
                 attrs: Dict[str, Union[List, int, str, Node, Attribute, Fact]] = None):
        super().__init__(kind, neg, attrs)

    def __repr__(self):
        return 'person'

    #     self.__age = age
    #     self.__sex = sex
    #     self.__name = name
    #     self.__nationality = nationality
    #
    # @property
    # def age(self):
    #     return self.__age
    #
    # @property
    # def sex(self):
    #     return self.__sex
    #
    # @property
    # def name(self):
    #     return self.__name
    #
    # @property
    # def nationality(self):
    #     return self.__nationality
    #
    # @age.setter
    # def age(self, age: str):
    #     self.__age = age
    #
    # @sex.setter
    # def sex(self, sex: str):
    #     self.__sex = sex
    #
    # @name.setter
    # def name(self, name: str):
    #     self.__name = name
    #
    # @nationality.setter
    # def nationality(self, nationality: str):
    #     self.__nationality = nationality
