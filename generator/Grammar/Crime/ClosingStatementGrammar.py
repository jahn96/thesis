"""
"If you have any information, we are asking you call Crime Stoppers @ 512-472-TIPS," Austin police said.

No arrests have been made.
The investigation into the shooting is ongoing, according to the sheriff's office.
Anyone with information is asked to contact authorities.
"""
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from generator.Grammar.Grammar import Grammar


class ClosingStatementGrammar(Grammar):
    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        # no arrests have been made
        arrest_grammar = """
            S -> NP VP
            NP -> NDT NNNS
        """

        if self.tense == 'present':
            arrest_grammar += """
                VP -> VVBP VVP
                VVBP -> 'have'
            """
        elif self.tense == 'past':
            arrest_grammar += """
                VP -> VVBD VVP
                VVBD -> 'had'
            """

        arrest_grammar += """
            NDT -> 'No'
            NNNS -> 'arrests'
            VVBP -> 'have'
            VVP -> VVBN VVP2
            
            VVBN -> 'been'
            VVP2 -> 'made'
        """

        arrest_abs_fact = Fact(
            subj=Object(kind=self.lemmatizer.lemmatize('arrests'), neg=True),
            event=Event(kind=self.stemmer.stem('made'), passive=True),
        )

        investigation_grammar = """
            S -> NP VP
            NP -> NNP NPP
            NNP -> NDT NNN
            NPP -> NIN NNP2
            NDT -> 'the'
            NNN -> 'investigation'
            NIN -> 'into'
            NNP2 -> NDT NNN2
            NNN2 -> 'shooting'
        """

        if self.tense == 'present':
            investigation_grammar += """
                VP -> VVBZ VADJP COMMA VPP
                VVBZ -> 'is'
            """
        elif self.tense == 'past':
            investigation_grammar += """
                VP -> VVBD VADJP COMMA VPP
                VVBD -> 'was'
            """

        investigation_grammar += """
            VADJP -> VJJ
            COMMA -> ','
            VPP -> VVBG VPP2

            VJJ -> 'ongoing'
            VVBG -> 'according'
            VPP2 -> VIN VNP

            VIN -> 'to'
            VNP -> VNP2 VNN

            VNP2 -> VDT VNN2 VPOS
            VNN -> 'office'
            VDT -> 'the'
            VNN2 -> 'sheriff'
            VPOS -> "'s"
        """

        investigation_abs_fact = Fact(
            subj=Object(kind='investigation', attrs={'phrase_mod': [Object(kind='into', attrs={'obj': 'shooting'}),
                                                                    Object(kind='according to', attrs={'obj':
                                                                                                           Object(
                                                                                                               kind='office',
                                                                                                               attrs={
                                                                                                                   'poss': 'sheriff'})})],
                                                     'adj_mod': 'ongoing'}),
        )

        contact_grammar = """
            S -> NP VP
            NP -> NNP NPP
            
            NNP -> NNN
            NPP -> NIN NNP2
            NNN -> 'Anyone'
            NIN -> 'with'
            NNP2 -> NNN2
            NNN2 -> 'information'
        """

        if self.tense == 'present':
            contact_grammar += """
                VP -> VVBZ VVP
                VVBZ -> 'is'
            """
        elif self.tense == 'past':
            contact_grammar += """
                VP -> VVBD VVP
                VVBD -> 'was'
            """

        contact_grammar += """
            VVP -> VVBN S2
            
            VVBN -> 'asked'
            S2 -> VP2
            VP2 -> VTO VVP2
            VTO -> 'to'
            VVP2 -> VVB VNP
            VVB -> 'contact'
            VNP -> VDT VNNS
            VDT -> 'the'
            VNNS -> 'authorities'
        """

        contact_abs_fact = Fact(
            subj=Person(kind='anyone', attrs={'phrase_mod': Object(kind='with', attrs={'obj': 'information'})}),
            event=Event(kind='asked', passive=True, attrs={'clause_comp': Event(kind='contact', attrs={'obj': 'authorities'})})
        )

        self.grammar = [arrest_grammar, investigation_grammar, contact_grammar]
        self.abstract_fact = []
