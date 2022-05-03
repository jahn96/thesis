from abc import ABC, abstractmethod
from typing import Union
# from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer

from utils import morphy


class Grammar(ABC):
    """
    Grammar class
    """
    @abstractmethod
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        if tense not in ['present', 'past']:
            print('tense should be either present or past!')
            exit(-1)

        self.__grammar: Union[str, list] = ''
        self.__tense = tense
        self.__metadata = metadata
        self.__grammar_type = grammar_type
        self.abstract_fact = None
        self.morphy = morphy
        self.num_text_int_map = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4
        }
        self.num_int_text_map = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four'
        }
        # self.stemmer = LancasterStemmer()
        # self.lemmatizer = WordNetLemmatizer()

    @property
    def tense(self):
        return self.__tense

    @property
    def grammar(self):
        return self.__grammar

    @property
    def grammar_type(self):
        return self.__grammar_type

    @property
    def metadata(self):
        return self.__metadata

    @grammar.setter
    def grammar(self, grammar):
        self.__grammar = grammar

    @metadata.setter
    def metadata(self, metadata):
        self.__metadata = metadata

    @abstractmethod
    def define_grammar(self):
        """
            Generate PCFG grammars
        """
        pass
