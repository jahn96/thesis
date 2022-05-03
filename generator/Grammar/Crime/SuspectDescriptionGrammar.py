from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class SuspectDescriptionGrammar(Grammar):
    """
    Grammar that describes the suspect
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        suspect_desc_grammar = """            
            S -> NP VP [1.0]
            COMMA -> ',' [1.0]
            
            NP -> NNP NPP [1.0]
            VP -> VVBD VADJP [1.0]
            
            NNP -> NDT NNNS [1.0]
            NPP -> NIN NNP2 [1.0]
            VVBD -> 'were' [1.0]
            VADJP -> VJJ [1.0]
            
            NDT -> 'the' [1.0]
            NNNS -> 'relationships' [1.0]
            NIN -> 'between' [1.0]
            NNP2 -> NNP3 NCC NNP4 [1.0]
            VJJ -> 'unclear' [1.0]
            
            NNP3 -> NDT NNN [1.0]
            NCC -> 'and' [1.0]
            NNP4 -> NDT NNN2 [1.0]
            
            NNN -> 'suspect' [1.0]
            NNN2 -> 'victim' [1.0]
        """

        # The relationships between the suspect and the victim were unclear.
        suspect_abs_fact = Fact(
            subj=Object(kind=self.morphy('relationships', 'noun'),
                        attrs={'phrase_mod': Phrase(kind='between',
                                                    attrs={'obj': Multiple(conj='and',
                                                                           nodes=[Person(kind='suspect'),
                                                                                  Person(kind='victim')]
                                                                           )
                                                           }
                                                    ),
                               'obj_mod': 'unclear'
                               }
                        )
        )
        self.grammar = suspect_desc_grammar
        self.abstract_fact = suspect_abs_fact
