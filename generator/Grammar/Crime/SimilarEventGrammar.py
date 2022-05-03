import random

from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


# TODO: add these grammars too
# The other mass shooting took place at the Columbiana Centre mall in Columbia.
# Fourteen people were injured in that shooting, and one person has been arrested.
# There was also another shooting in Pittsburgh early Sunday that left two people dead and several others injured at a large party.

class SimilarEventGrammar(Grammar):
    """
    Grammar that outputs similar instance of event
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = self.metadata['event']
        location = self.metadata['location']

        if event != 'shooting' or location.lower() not in ['america', 'us', 'new york']:
            self.grammar = ''
            self.abstract_fact = None
            return

        count = str(random.randint(100, 200))
        state = 'New York'
        day = 'Monday'

        similar_event_grammar = f"""
            S -> NP-TMP COMMA NP VP [1.0]
            
            NP-TMP -> NDT NNN [1.0]
            COMMA -> ',' [1.0]
            NP -> NCD NNNS [1.0]
            VP -> VVBD VPP COMMA VPP2 VNP-TMP [1.0]
            
            NDT -> 'this' [1.0]
            NNN -> 'weekend' [1.0]
            NCD -> 'two' [1.0]
            NNNS -> 'shootings' [1.0]
            VVBD -> 'happened' [1.0]
            VPP -> VIN VNP [1.0]
            VPP2 -> VIN2 VNP2 [1.0]
            VNP-TMP -> VNN [1.0]
            
            VIN -> 'in' [1.0]
            VNP -> VSTATE [1.0]
            VIN2 -> 'with' [1.0]
            VNP2 -> VNP3 VPP3 [1.0]
            VNN -> 'afternoon' [1.0]
            
            VSTATE -> '{state}' [1.0]
            VNP3 -> VDT VNNS [1.0]
            VPP3 -> VIN3 VNP4 [1.0]
            
            VDT -> 'no' [1.0]
            VNNS -> 'fatalities' [1.0]
            VIN3 -> 'in' [1.0]
            VNP4 -> VNP5 VPP4 [1.0]
            
            VNP5 -> VDT2 VNN2 [1.0]
            VPP4 -> VRB VIN4 VNP6 [1.0]
            
            VDT2 -> 'either' [1.0]
            VNN2 -> 'incident' [1.0]
            VRB -> 'as' [1.0]
            VIN4 -> 'of' [1.0]
            VNP6 -> VNNP [1.0]
            VNNP -> '{day}' [1.0]
        """

        # This weekend, two shootings happened in [US_STATE], with no fatalities in either incident as of [DAY] afternoon.
        similar_event_abstract_fact = Fact(
            subj=Object(kind=self.morphy('shootings', 'noun'), attrs={'count': 'two'}),
            event=Event(kind=self.morphy('happened', 'verb'),
                        attrs={'time': 'weekend',
                               'location': state,
                               'phrase_mod': Phrase(kind='with', attrs={
                                   'obj': Object(kind=self.morphy('fatalities', 'noun'), neg=True,
                                                 attrs={'event': Object(kind='incident',
                                                                        attrs={'obj_mod': 'either',
                                                                               'phrase_mod': Phrase(kind='as of',
                                                                                                    attrs={
                                                                                                        'obj': Object(
                                                                                                            kind='afternoon',
                                                                                                            attrs={
                                                                                                                'day': day})})})})})})
        )

        similar_event_grammar_2 = """
            S -> NP ADVP VP [1.0]
            
            NP -> NDT NNNS [1.0]
            ADVP -> ARB [1.0]
            VP -> VVBP VNP [1.0]
            
            NDT -> 'these' [1.0]
            NNNS -> 'shootings' [1.0]
            ARB -> 'also' [1.0]
            VVBP -> 'follow' [1.0]
            VNP -> VNP2 VPP [1.0]
            
            VNP2 -> VDT VNN [1.0]
            VPP -> VIN VNP3 [1.0]
            
            VDT -> 'a' [1.0]
            VNN -> 'scourge' [1.0]
            VIN -> 'of' [1.0]
            VNP3 -> VNP4 SBAR [1.0]
            
            VNP4 -> VNN2 VNN3 [1.0]
            SBAR -> WHNP S2 [1.0]
            
            VNN2 -> 'gun' [1.0]
            VNN3 -> 'violence' [1.0]
            WHNP -> WDT [1.0]
            S2 -> VP2 [1.0]
            
            WDT -> 'that' [1.0]
            VP2 -> VVBZ VVP [1.0]
            
            VVBZ -> 'has' [1.0]
            VVP -> VVBN VVP2 [1.0]
            
            VVBN -> 'been' [1.0]
            VVP2 -> VVBG VNP5 [1.0]
            
            VVBG -> 'plaguing' [1.0]
            VNP5 -> VNP6 VPP2 [1.0]
            
            VNP6 -> VDT2 VNNP [1.0]
            VPP2 -> VIN2 VNP7 [1.0]
            
            VDT2 -> 'the' [1.0]
            VNNP -> 'US' [1.0]
            VIN2 -> 'in' [1.0]
            VNP7 -> VDT2 VJJ VJJ2 VNNS [1.0]
            
            VJJ -> 'last' [1.0]
            VJJ2 -> 'few' [1.0]
            VNNS -> 'weeks' [1.0]
        """

        # These shootings also follow a scourge of gun violence that has been plaguing the US in the last few weeks.
        similar_event_abstract_fact_2 = Fact(
            subj=Object(kind=self.morphy('shootings', 'noun')),
            event=Event(kind=self.morphy('follow', 'verb')),
            obj=Object(kind=self.morphy('scourge', 'noun'),
                       attrs={'phrase_mod': Phrase(kind='of',
                                                   attrs={'obj': Object(kind='violence',
                                                                        attrs={'obj_mod': 'gun', 'clause_rel': Fact(
                                                                            subj=Object(kind='violence'), event=Event(
                                                                                kind=self.morphy('plaguing', 'verb'),
                                                                                attrs={'obj': 'US', 'time': Object(
                                                                                    kind=self.morphy('weeks', 'noun'),
                                                                                    attrs={
                                                                                        'obj_mod': Modifier(kind='few',
                                                                                                            attrs={
                                                                                                                'mod_mod': 'last'})})}))})})})
        )

        similar_event_grammar_3 = f"""
            S -> PP COMMA NP VP [1.0]
            
            PP -> PIN PNP [1.0]
            COMMA -> ',' [1.0]
            NP -> NEX [1.0]
            VP -> VVBP VVP [1.0]
            
            PIN -> 'to' [1.0]
            PNP -> PNN [1.0]
            NEX -> 'there' [1.0]
            VVBP -> 'have' [1.0]
            VVP -> VVBN VNP VNP-TMP COMMA VPP [1.0]
            
            PNN -> 'date' [1.0]
            VVBN -> 'existed' [1.0]
            VNP -> VQP VNNS [1.0]
            VNP-TMP -> VADVP VDT VNN [1.0]
            VPP -> VVBG VPP2 [1.0]
            
            VQP -> VJJR VIN VCD [1.0]
            VNNS -> 'shootings' [1.0]
            VADVP -> VRB VRB2 [1.0]
            VDT -> 'this' [1.0]
            VNN -> 'year' [1.0]
            VVBG -> 'according' [1.0]
            VPP2 -> VIN2 VNP2 [1.0]
            
            VJJR -> 'more' [1.0]
            VIN -> 'than' [1.0]
            VCD -> '{count}' [1.0]
            
            VRB -> 'so' [1.0]
            VRB2 -> 'far' [1.0]
            VIN2 -> 'to' [1.0]
            VNP2 -> VDT2 VNNP VNNP2 VNNP3 [1.0]
            
            VDT2 -> 'the' [1.0]
            VNNP -> 'Gun' [1.0]
            VNNP2 -> 'Violence' [1.0]
            VNNP3 -> 'Archive' [1.0]
        """

        # To date, there have existed more than [COUNT] shootings so far this year, according to the Gun Violence Archive.
        similar_event_abstract_fact_3 = Fact(
            event=Event(kind=self.morphy('existed', 'verb')),
            obj=Object(kind=self.morphy('shootings', 'noun'),
                       attrs={'count': Modifier(kind=count, attrs={'mod_mod': 'more than'}), 'period': Object('year'),
                              'phrase_mod': Phrase(kind='according to', attrs={'obj':
                                  Object(
                                      kind='Gun Violence Archive')})})
        )

        self.grammar = [similar_event_grammar, similar_event_grammar_2, similar_event_grammar_3]
        self.abstract_fact = [similar_event_abstract_fact, similar_event_abstract_fact_2, similar_event_abstract_fact_3]

# These shootings also follow a scourge of gun violence that has been plaguing the US in the last few weeks.
