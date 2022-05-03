import random

from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class CrimeReasonGrammar(Grammar):
    """
    Grammar that outputs the charge of a criminal
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = self.metadata['event']
        num_attackers = self.metadata['num_attackers']

        count = self.num_int_text_map[random.randint(1, num_attackers)]
        action_verb = 'happened'
        action = ''

        if event == 'shooting':
            action = 'gunshots'
            weapon = 'handguns'
            action_verb = 'fired'
        elif event == 'stab':
            action = 'stab'
            weapon = 'knives'

        reason_grammar = f"""
            S -> NP VP [1.0]
            NP -> NNNS [1.0]
            VP -> VVBP VADVP VVP [1.0]
            
            NNNS -> 'investigators' [1.0]
            VVBP -> 'are' [1.0]
            VADVP -> VRB [1.0]
            VVP -> VVBG S2 [1.0]
            
            VRB -> 'still' [1.0]
            VVBG -> 'working' [1.0]
            S2 -> VP2 [1.0]
            
            VP2 -> VTO VVP2 [1.0]
            VTO -> 'to' [1.0]
            VVP2 -> VVB SBAR [1.0]
            
            VVB -> 'determine' [1.0]
            SBAR -> WHNP S3 [1.0]
            
            WHNP -> WP [1.0]
            S3 -> VP3 [1.0]
            
            WP -> 'what' [1.0]
            VP3 -> VVBD VPRT VPP [1.0]
            
            VVBD -> 'led' [1.0]
            VPRT -> VRP [1.0]
            VPP -> VIN VNP [1.0]
            
            VRP -> 'up' [1.0]
            VIN -> 'to' [1.0]
            VNP -> VDT VNN [1.0]
            
            VDT -> 'the' [1.0]
            VNN -> '{event}' [1.0]
        """

        # Investigators are still working to determine what led up to the shooting.
        reason_abstract_fact = Fact(
            subj=Person(kind=self.morphy('investigators', 'noun')),
            event=Event(kind=self.morphy('working', 'verb'), attrs={
                'event_mod': 'still',
                'phrase_mod': Phrase(kind='to', attrs={
                    'event': Event(kind='determine', attrs={'obj': Fact(
                        subj=Object(kind='what'),
                        event=Event(kind=self.morphy('led', 'verb') + ' up', attrs={'obj': Object(kind=event)})
                    )})
                })
            })
        )

        reason_grammar_2 = f"""
            S -> NP COMMA ADVP COMMA VP [1.0]
            
            NP -> NPRP [1.0]
            COMMA -> ',' [1.0]
            ADVP -> ARB [1.0]
            VP -> VVBD SBAR [1.0]
            
            NPRP -> 'they' [1.0]
            ARB -> 'however' [1.0]
            VVBD -> 'said' [1.0]
            SBAR -> S2 [1.0]
            
            S2 -> NP2 VP2 [1.0]
            
            NP2 -> NPP [1.0]
            VP2 -> VVBD2 SBAR2 [1.0]
            
            NPP -> NDT NNP2 [1.0]
            VVBD2 -> 'occurred' [1.0]
            SBAR2 -> WHADVP S3 [1.0]
            
            NDT -> 'some' [1.0]
            NNP2 -> NNN2 [1.0]
            WHADVP -> WRB [1.0]
            S3 -> NP3 VP3 [1.0]
            
            NNN2 -> 'altercation' [1.0]
            WRB -> 'when' [1.0]
            NP3 -> NNNS [1.0]
            VP3 -> VVBD3 VVP [1.0]
            
            NNNS -> '{action}' [1.0]
            VVBD3 -> 'were' [1.0]
            VVP -> VVBN [1.0]
            VVBN -> '{action_verb}' [1.0] 
        """

        reason_abstract_fact_2 = Fact(
            subj=Person(kind='they'),
            event=Event(kind=self.morphy('said', 'verb'),
                        attrs={'event_mod': 'however', 'obj': Fact(
                            subj=Object(kind='altercation'),
                            event=Event(kind=self.morphy('occurred', 'verb'), attrs={
                                'clause_adv': Clause(connective='when',
                                                     subj=Object(kind=self.morphy(action, 'noun')),
                                                     event=Event(kind=self.morphy(action_verb, 'verb'), passive=True)
                                                     )
                            })
                        )})
        )

        reason_grammar_3 = f"""
            S -> NP VP [1.0] 
            NP -> NNNS [1.0] 
            VP -> VVBP SBAR [1.0] 
            
            NNNS -> 'police' [1.0] 
            VVBP -> 'believe' [1.0] 
            SBAR -> S2 [1.0] 
            
            S2 -> NP2 VP2 [1.0] 
            
            NP2 -> NNP NPP [1.0] 
            VP2 -> VVBZ VVP [1.0] 
            
            NNP -> NDT NNN [1.0] 
            NPP -> NIN NNP2 [1.0] 
            VVBZ -> 'is' [1.0] 
            VVP -> VVBN VPP [1.0] 
            
            NDT -> 'the' [1.0] 
            NNN -> 'motive' [1.0] 
            NIN -> 'for' [1.0] 
            NNP2 -> NDT NNN2 [1.0] 
            VVBN -> 'connected' [1.0] 
            VPP -> VIN VNP [1.0] 
            
            NNN2 -> '{event}' [1.0] 
            VIN -> 'to' [1.0] 
            VNP -> VNP2 VPP2 [1.0] 
            
            VNP2 -> VDT VJJ VNN [1.0] 
            VPP2 -> VIN2 VNP3 [1.0] 
            
            VDT -> 'an' [1.0] 
            VJJ -> 'ongoing' [1.0] 
            VNN -> 'dispute' [1.0] 
            VIN2 -> 'between' [1.0] 
            VNP3 -> VDT2 VNNS VCC VDT2 VNNS2 [1.0] 
            
            VDT2 -> 'the' [1.0] 
            VNNS -> 'suspect' [1.0]
            VCC -> 'and' [1.0]
            VNNS2 -> 'victim' [1.0]
        """

        reason_abstract_fact_3 = Fact(
            subj=Person(kind=self.morphy('police', 'noun')),
            event=Event(kind=self.morphy('believe', 'verb')),
            obj=Fact(
                subj=Object(kind=self.morphy('motive', 'noun'),
                            attrs={'phrase_mod': Phrase(kind='for', attrs={'obj': event})}),
                event=Event(kind=self.morphy('connected', 'verb'),
                            passive=True,
                            attrs={'phrase_mod':
                                       Phrase(kind='to',
                                              attrs={'obj':
                                                         Object(kind=self.morphy('dispute', 'noun'),
                                                                attrs={'obj_mod': 'ongoing',
                                                                       'phrase_mod': Phrase(kind='between',
                                                                                            attrs={'obj':
                                                                                                       Multiple(
                                                                                                           conj='and',
                                                                                                           nodes=[
                                                                                                               Person(
                                                                                                                   kind=self.morphy(
                                                                                                                       'suspect',
                                                                                                                       'noun')),
                                                                                                               Person(
                                                                                                                   kind=self.morphy(
                                                                                                                       'victim',
                                                                                                                       'noun'))])})})})})
            )
        )

        reason_grammar_4 = f"""
            S -> NP VP [1.0] 
            
            NP -> NCD NNNS [1.0] 
            VP -> VVBP VVP [1.0] 
            
            NCD -> '{count}' [1.0] 
            NNNS -> '{self.morphy(weapon, 'noun') if count == 'one' else weapon}' [1.0] 
            VVBP -> 'have' [1.0] 
            VVP -> VVBN VVP2 [1.0] 
            
            VVBN -> 'been' [1.0] 
            VVP2 -> VVBN2 SBAR [1.0] 
            
            VVBN2 -> 'seized' [1.0] 
            SBAR -> IN S2 [1.0] 
            
            IN -> 'that' [1.0] 
            S2 -> VP2 [1.0] 
            
            VP2 -> SBAR2 [1.0] 
            SBAR2 -> S3 [1.0] 
            
            S3 -> VP3 [1.0] 
            
            VP3 -> VVBD VVP3 [1.0] 
            VVBD -> 'were' [1.0] 
            VVP3 -> VVBN3 VPP [1.0] 
            
            VVBN3 -> 'used' [1.0] 
            VPP -> VIN VNP [1.0] 
            VIN -> 'in' [1.0] 
            
            VNP -> VDT VNN [1.0] 
            VDT -> 'the' [1.0] 
            VNN -> '{event}' [1.0] 
        """

        reason_abstract_fact_4 = Fact(
            subj=Object(kind=self.morphy(weapon, 'noun'), attrs={'count': count}),
            event=Event(kind=self.morphy('seized', 'verb'), passive=True, attrs={
                # 'event_mod': Fact(subj=Person(self.morphy('police', 'noun')), event=Event(kind=self.morphy('believe', 'verb'))),
                'clause_rel': Fact(subj=Object(kind=self.morphy(weapon, 'noun')),
                                   event=Event(kind=self.morphy('used', 'verb'),
                                               passive=True,
                                               attrs={'phrase_mod': Phrase(kind='in', attrs={'obj': event})}))
            }),
        )

        self.grammar = [reason_grammar, reason_grammar_2, reason_grammar_3, reason_grammar_4]
        self.abstract_fact = [reason_abstract_fact, reason_abstract_fact_2, reason_abstract_fact_3,
                              reason_abstract_fact_4]
