# Amari's attorney, Todd Rutherford, told Sunday his client "did not do anything to bring about the trouble" and was attacked by two people shooting at him at the mall.
from Attributes.DayAttribute import DayAttribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class AttorneyGrammar(Grammar):
    """
    Grammar that outputs the quote from an attorney
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        count = self.metadata['num_attackers']
        location = self.metadata['location']
        event = self.metadata['event']

        attorney_grammar = f"""
            S -> NP VP [1.0]
            
            NP -> NNP NNN [1.0]
            VP -> VVBD VNP-TMP VSBAR [1.0]
            
            NNP -> NDT NNN2 NPOS [1.0]
            NNN -> 'attorney' [1.0]
            VVBD -> 'said' [1.0]
            VNP-TMP -> VIN5 VNNP [1.0]
            VSBAR -> S2 [1.0]
            
            NDT -> 'the' [1.0]
            NNN2 -> 'victim' [1.0]
            NPOS -> "'s" [1.0]
            VIN5 -> 'on' [1.0]
            VNNP -> '[DAY]' [1.0]
            S2 -> NP2 VP2 [1.0]
            
            NP2 -> NPRP NNN3 [1.0]
            VP2 -> VVP VCC VVP2 [1.0]
            
            NPRP -> '"his' [1.0]
            NNN3 -> 'client' [1.0]
            VVP -> VVBD2 VRB VVP3 [1.0]
            VCC -> 'and' [1.0]
            VVP2 -> VVBD3 VVP4 [1.0]
            
            VVBD2 -> 'did' [1.0]
            VRB -> 'not' [1.0]
            VVP3 -> VVB VNP S3 [1.0]
            VVBD3 -> 'was' [1.0]
            VVP4 -> VVBN VPP [1.0]
            
            VVB -> 'do' [1.0]
            VNP -> VNN [1.0]
            S3 -> VP3 [1.0]
            VVBN -> 'attacked' [1.0]
            VPP -> VIN VNP2 [1.0]
            
            VNN -> 'anything' [1.0]
            VP3 -> VTO VVP5 [1.0]
            VIN -> 'by' [1.0]
            VNP2 -> VNP3 VVP6 [1.0]
            
            VTO -> 'to' [1.0]
            VVP5 -> VVB2 VPP2 [1.0]
            VNP3 -> VCD VNNS [1.0]
            VVP6 -> VVBG VPP3 VPP4 [1.0]
            
            VVB2 -> 'bring' [1.0]
            VPP2 -> VIN2 VNP4 [1.0]
            VCD -> '{count}' [1.0]
            VNNS -> 'people' [1.0]
            VVBG -> '{event}' [1.0]
            VPP3 -> VIN3 VNP5 [1.0]
            VPP4 -> VIN4 VNP6 [1.0]
            
            VIN2 -> 'about' [1.0]
            VNP4 -> VDT VNN2 [1.0]
            VIN3 -> 'at' [1.0]
            VNP5 -> VPRP [1.0]
            VIN4 -> 'at' [1.0]
            VNP6 -> VDT VNN3 [1.0]
            
            VDT -> 'the' [1.0]
            VNN2 -> 'trouble' [1.0]
            VPRP -> 'him' [1.0]
            VNN3 -> '{location}."'  [1.0]
        """

        attorney_abstract_fact = Fact(
            subj=Person(kind=self.morphy('attorney', 'noun'), attrs={'obj_pos': 'victim'}),
            event=Event(kind=self.morphy('said', 'verb'), attrs={'day': DayAttribute()}),
            obj=Fact(
                subj=Person(kind=self.morphy('client', 'noun'), attrs={'obj_pos': 'his'}),
                event=Multiple(conj='and',
                               nodes=[Event(kind=self.morphy('do', 'verb'), neg=True, attrs={
                                   'obj': Object(kind='anything', attrs={'phrase_mod': Phrase(kind='to', attrs={
                                       'event': Event(kind='bring', attrs={
                                           'phrase_mod': Phrase(kind='about', attrs={'obj': 'trouble'})})})})}),
                                      Event(kind=self.morphy('attacked', 'verb'), passive=True,
                                            attrs={'obj': Person(kind=self.morphy('people', 'noun'),
                                                                 attrs={'count': count,
                                                                        'clause_part': Fact(subj=Person(
                                                                            kind=self.morphy('people', 'noun')),
                                                                                            event=Event(
                                                                                                kind=self.morphy(
                                                                                                    event, 'verb'),
                                                                                                attrs={
                                                                                                    'location': location}),
                                                                                            obj=Person(kind='him'))
                                                                        }
                                                                 )})]),
            )
        )

        self.grammar = attorney_grammar
        self.abstract_fact = attorney_abstract_fact
