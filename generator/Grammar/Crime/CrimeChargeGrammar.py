from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class CrimeChargeGrammar(Grammar):
    """
    Grammar that outputs the charge of a criminal
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        charge_grammar = """
        """

        charge_abstract_fact = Fact()

        self.grammar = charge_grammar
        self.abstract_fact = charge_abstract_fact
