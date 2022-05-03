"""
"If you have any information, we are asking you call Crime Stoppers @ 512-472-TIPS," Austin police said.

No arrests have been made.
The investigation into the shooting is ongoing, according to the sheriff's office.
Anyone with information is asked to contact authorities.
"""
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class ClosingStatementGrammar(Grammar):
    """
    Grammar that outputs the closing statement of a crime article
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = self.metadata['event']

        # no arrests have been made
        arrest_grammar = """
            S -> NP VP [1.0]
            NP -> NDT NNNS [1.0]
        """

        if self.tense == 'present':
            arrest_grammar += """
                VP -> VVBP VVP [1.0]
                VVBP -> 'have' [1.0]
            """
        elif self.tense == 'past':
            arrest_grammar += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'had' [1.0]
            """

        arrest_grammar += """
            NDT -> 'No' [1.0]
            NNNS -> 'arrests' [1.0]
            VVBP -> 'have' [1.0]
            VVP -> VVBN VVP2 [1.0]
            
            VVBN -> 'been' [1.0]
            VVP2 -> 'made' [1.0]
        """

        arrest_abs_fact = Fact(
            subj=Object(kind=self.morphy('arrests', 'noun'), neg=True),
            event=Event(kind=self.morphy('made', 'verb'), passive=True),
        )

        investigation_grammar = f"""
            S -> NP VP [1.0]
            NP -> NNP NPP [1.0]
            NNP -> NDT NNN [1.0]
            NPP -> NIN NNP2 [1.0]
            NDT -> 'the' [1.0]
            NNN -> 'investigation' [1.0]
            NIN -> 'into' [1.0]
            NNP2 -> NDT NNN2 [1.0]
            NNN2 -> '{event}' [1.0]
        """

        if self.tense == 'present':
            investigation_grammar += """
                VP -> VVBZ VADJP COMMA VPP [1.0]
                VVBZ -> 'is' [1.0]
            """
        elif self.tense == 'past':
            investigation_grammar += """
                VP -> VVBD VADJP COMMA VPP [1.0]
                VVBD -> 'was' [1.0]
            """

        investigation_grammar += """
            VADJP -> VJJ [1.0]
            COMMA -> ',' [1.0]
            VPP -> VVBG VPP2 [1.0]

            VJJ -> 'ongoing' [1.0]
            VVBG -> 'according' [1.0]
            VPP2 -> VIN VNP [1.0]

            VIN -> 'to' [1.0]
            VNP -> VDT VNN [1.0]
            
            VDT -> 'the' [1.0]
            VNN -> 'police' [1.0]
        """

        investigation_abs_fact = Fact(
            subj=Object(kind='investigation', attrs={
                'phrase_mod': Multiple(conj='', nodes=[
                    Phrase(kind='into', attrs={'obj': event}), Phrase(kind='according to', attrs={'obj':
                        Object(
                            kind='police')})]),
                'obj_mod': Modifier(kind='ongoing')}
            ),
        )

        contact_grammar = """
            S -> NP VP [1.0]
            NP -> NNP NPP [1.0]
            
            NNP -> NNN [1.0]
            NPP -> NIN NNP2 [1.0]
            NNN -> 'Anyone' [1.0]
            NIN -> 'with' [1.0]
            NNP2 -> NNN2 [1.0]
            NNN2 -> 'information' [1.0]
        """

        if self.tense == 'present':
            contact_grammar += """
                VP -> VVBZ VVP [1.0]
                VVBZ -> 'is' [1.0]
            """
        elif self.tense == 'past':
            contact_grammar += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'was' [1.0]
            """

        contact_grammar += """
            VVP -> VVBN S2 [1.0]
            
            VVBN -> 'asked' [1.0]
            S2 -> VP2 [1.0]
            VP2 -> VTO VVP2 [1.0]
            VTO -> 'to' [1.0]
            VVP2 -> VVB VNP [1.0]
            VVB -> 'contact' [1.0]
            VNP -> VDT VNNS [1.0]
            VDT -> 'the' [1.0]
            VNNS -> 'authorities' [1.0]
        """

        contact_abs_fact = Fact(
            subj=Person(kind='anyone', attrs={'phrase_mod': Phrase(kind='with', attrs={'obj': 'information'})}),
            event=Event(kind='asked', passive=True,
                        attrs={'phrase_mod': Phrase(kind='to', attrs={
                            'event': Event(kind='contact', attrs={'obj': 'authorities'})})})
        )

        self.grammar = [contact_grammar]
        self.abstract_fact = [contact_abs_fact]
