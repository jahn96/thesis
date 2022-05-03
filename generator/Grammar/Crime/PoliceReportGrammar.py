from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar

# TODO: add condolence from police
from generator.Grammar.grammar_utils import get_next_day

"""
"Our thoughts and prayers are with his family and also with all the families and our shooting victims as a result of this incident," Col. Bill Bryant of the Arkansas State Police told reporters.
"""


class PoliceReportGrammar(Grammar):
    """
    Grammar that defines the police report of an event
    """

    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = ''

        if self.grammar_type == 1:
            if not self.metadata:
                print('Event must be passed as a metadata!')
                print('The place this event happened should be passed as a metadata!')
                print('The city this event happened should be passed as a metadata!')
                print('The day this event happened should be passed as a metadata!')
                print('The place_mod that modifies place should be passed as a metadata!')
                exit(-1)

            if 'event' not in self.metadata:
                print('Event must be passed as a metadata!')
                exit(-1)
            if 'place' not in self.metadata:
                print('The place this event happened should be passed as a metadata!')
                exit(-1)
            if 'place_mod' not in self.metadata:
                print('The place_mod that modifies place should be passed as a metadata!')
                exit(-1)
            if 'city' not in self.metadata:
                print('The city this event happened should be passed as a metadata!')
                exit(-1)
            if 'day' not in self.metadata:
                print('The date this event happened should be passed as a metadata!')
                exit(-1)

            event = self.metadata['event']
            place = self.metadata['place']  # such as restaurant, bar, or lounge
            place_mod = self.metadata['place_mod']
            city = self.metadata['city']
            day = self.metadata['day']

            next_day = get_next_day(day)

            police_report_grammar = f"""
                S -> S2 COMMA NP VP [1.0]
                S2 -> NP2 VP2 [1.0]
                
                COMMA -> ',' [1.0]
                NP -> NNNS [1.0]
                VP -> VVBD [1.0]
                NP2 -> NNP NVP [1.0]
                VP2 -> VVBD2 VVP [1.0]
                
                NNNS -> 'police' [1.0]
                VVBD -> 'said' [1.0]
                NNP -> NDT NNN [1.0]
                NVP -> VVBN VPP VIN5 VNP-TMP [1.0]
                VVBD2 -> 'was' [1.0]
                VVP -> VVBN2 VPP2 VIN5 VNP-TMP2 [1.0]
                
                NDT -> '"[ARTICLE]' [1.0]
                NNN -> 'man' [1.0]
                VVBN -> 'suspected' [1.0]
                VPP -> VIN VNP [1.0]
                VNP-TMP -> VNNP [1.0]
                VVBN2 -> 'taken' [1.0]
                VPP2 -> VIN2 VNP2 [1.0]
                VNP-TMP2 -> VNNP2 [1.0]
                VIN5 -> 'on' [1.0]
                
                VIN -> 'in' [1.0]
                VNP -> VNP3 VPP3 [1.0]
                VNNP -> '{day}' [1.0]
                VIN2 -> 'into' [1.0]
                VNP2 -> VNN [1.0]
                VNNP2 -> '{next_day}"' [1.0]
                
                VNP3 -> VDT VJJ2 VNN2 [1.0]
                VPP3 -> VIN3 VNP4 [1.0]
                VNN -> 'custody.' [1.0]
                
                VDT -> '[ARTICLE]' [1.0]
                VJJ2 -> 'deadly' [1.0]
                VNN2 -> '{event}' [1.0]
                VIN3 -> 'at' [1.0]
                VNP4 -> VNP5 VPP4 [1.0]
                
                VNP5 -> VDT VJJ3 VNN3 [1.0]
                VPP4 -> VIN4 VNP6 [1.0]
                
                VJJ3 -> '{place_mod}' [1.0]
                VNN3 -> '{place}' [1.0]
                VIN4 -> 'in' [1.0]
                VNP6 -> VNNP3 [1.0]
                VNNP3 -> '{city}' [1.0]
            """

            # A man suspected in a deadly shooting at a hookah lounge in Blacksburg on Friday was taken into custody on Saturday, police said.
            abstract_fact = Fact(subj=Person(kind='police'),
                                 event=Event(kind=self.morphy('said', 'verb')),
                                 obj=Fact(
                                     subj=Person(kind='man',
                                                 attrs={
                                                     'clause_rel': Fact(
                                                         subj=Person(kind='man'),
                                                         event=Event(kind=self.morphy('suspected', 'verb'),
                                                                     attrs={
                                                                         'phrase_mod':
                                                                             Phrase(kind='in',
                                                                                    attrs={'obj':
                                                                                        Object(
                                                                                            kind=event,
                                                                                            attrs={
                                                                                                'obj_mod': 'deadly',
                                                                                                'place': Object(
                                                                                                    kind=place,
                                                                                                    attrs={
                                                                                                        'obj_mod': place_mod,
                                                                                                        'location': city
                                                                                                    }
                                                                                                ),
                                                                                                'day': day,
                                                                                            })}),
                                                                     }))}),
                                     event=Event(
                                         kind=self.morphy('taken', 'verb'),
                                         passive=True,
                                         attrs={
                                             'phrase_mod': Phrase(kind='into', attrs={'obj': 'custody'}),
                                             'day': next_day})))

            self.grammar = [police_report_grammar]
            self.abstract_fact = [abstract_fact]

        elif self.grammar_type == 2:

            if not self.metadata:
                print('Event must be passed as a metadata!')
                exit(-1)

            if 'event' not in self.metadata:
                print('Event must be passed as a metadata!')
                exit(-1)

            event = self.metadata['event']

            grammar = f"""
                S -> S2 COMMA NP VP [1.0]
                
                S2 -> NP2 VP2 [1.0]
                COMMA -> ',' [1.0]
                NP -> NNNS [1.0]
                VP -> VVBD [1.0]
                
                NP2 -> NP3 NSBAR [1.0]
                VP2 -> VVBP VADVP VVP [1.0]
                NNNS -> 'police' [1.0]
                VVBD -> 'said' [1.0]
                
                NP3 -> NDT NNNS2 NCC NNS3 [1.0]
                NSBAR -> NWHNP S3 [1.0]
                VVBP -> 'are' [1.0]
                VADVP -> VRB [1.0]
                VVP -> VVBG VVP2 [1.0]
                
                NDT -> '"The' [1.0]
                NNNS2 -> 'facts' [1.0]
                NCC -> 'and' [1.0]
                NNS3 -> 'circumstances' [1.0]
                NWHNP -> NWDT [1.0]
                S3 -> VP3 [1.0]
                VRB -> 'still' [1.0]
                VVBG -> 'being' [1.0]
                VVP2 -> VVBN [1.0]
                
                NWDT -> 'that' [1.0]
                VP3 -> VVBD2 VPRT VPP [1.0]
                VVBN -> 'determined."' [1.0]
                
                VVBD2 -> 'led' [1.0]
                VPRT -> VRP [1.0]
                VPP -> VIN VNP [1.0]
                
                VRP -> 'up' [1.0]
                VIN -> 'to' [1.0]
                VNP -> VDT VNN [1.0]
                VDT -> 'this' [1.0]
                VNN -> '{event}' [1.0]
            """

            # TODO: NOTE: Event should have subj/obj attribute
            # "The facts and circumstances that led up to this shooting are still (being) determined," police said.
            abstract_fact = Fact(subj=Person(kind='police'),
                                 event=Event(kind=self.morphy('said', 'verb')),
                                 obj=Fact(
                                     subj=Multiple(conj='and', nodes=[
                                         Object(kind=self.morphy('facts', 'noun')),
                                         Object(kind=self.morphy('circumstances', 'noun'))
                                     ], attrs={
                                         'clause_rel':
                                             Fact(
                                                 subj=Object(kind='facts and circumstances'),
                                                 event=Event(kind=self.morphy('led', 'verb') + ' up', attrs={
                                                     'obj': event
                                                 }))
                                     }),
                                     event=Event(kind=self.morphy('determined', 'verb'),
                                                 passive=True,
                                                 attrs={'event_mod': 'still'}))
                                 )
            self.grammar = [grammar]
            self.abstract_fact = [abstract_fact]

        # TODO: Spacy can't parse the right (subject, verb, and object) relations for this
        elif self.grammar_type == 3:
            # A suspect has been apprehended after a shooting in Northern California on Wednesday night killed one person and wounded several people.
            grammar = """
                S -> NP VP [1.0]
                CC -> 'and' [1.0]
                
                NP -> NDT NNN [1.0]
                VP -> VVBZ VVP [1.0]                
                
                NDT -> 'a' [1.0]
                NNN -> 'suspect' [1.0]
                VVBZ -> 'has' [1.0]
                VVP -> VVBN VVP2 [1.0]
                
                VVBN -> 'been' [1.0]
                VVP2 -> VVBN2 SBAR [1.0]
                
                VVBN2 -> 'apprehended' [1.0]
                
                SBAR -> VIN S3 [1.0]
                VIN -> 'after' [1.0]
                S3 -> NP3 VP3 [1.0]
                
                NP3 -> NNP NPP [1.0]
                VP3 -> VVP3 CC VVP4 [1.0]
                
                NNP -> NDT2 NNN2 [1.0]
                NPP -> NIN NNP2 [1.0]
                VVP3 -> VVBD2 VNP [1.0]
                VVP4 -> VVBD3 VNP2 [1.0]
                
                NDT2 -> 'the' [1.0]
                NNN2 -> 'shooting' [1.0]
                NIN -> 'in' [1.0]
                NNP2 -> NNP3 NPP2 NNP-TMP [1.0]
                VVBD2 -> 'killed' [1.0]
                VNP -> VCD VNN [1.0]
                VVBD3 -> 'wounded' [1.0]
                VNP2 -> VJJ VNNS [1.0]
                
                NNP3 -> 'Northern California' [1.0]
                NPP2 -> NIN2 NNP4 [1.0]
                NNP-TMP -> NNN3 [1.0]
                VCD -> 'one' [1.0]
                VNN -> 'person' [1.0]
                VJJ -> 'several' [1.0]
                VNNS -> 'people' [1.0]
                
                NIN2 -> 'on' [1.0]
                NNP4 -> NNNP [1.0]
                NNN3 -> 'night' [1.0]
                NNNP -> 'Wednesday' [1.0]
            """

            # A suspect has been apprehended after the shooting in Northern California on Wednesday night killed one person and wounded several people.
            abstract_fact = Fact(
                subj=Person(kind='suspect'),
                event=Event(kind='apprehend', passive=True, attrs={
                    'clause_mod': Clause(connective='after',
                                         subj=Object(kind='shooting',
                                                     attrs={
                                                         'location': 'Northern California',
                                                         'time': Object(kind='night', attrs={'day': 'Wednesday'})}),
                                         event=Multiple(conj='and',
                                                        nodes=[Event(kind=self.morphy('killed', 'verb'),
                                                                     attrs={'obj': Person(kind='person',
                                                                                          attrs={'count': 'one'})}),
                                                               Event(kind=self.morphy('wounded', 'verb'), attrs={
                                                                   'obj': Person(kind='people',
                                                                                 attrs={'count': 'several'})})]),
                                         )
                })
            )

            self.grammar = [grammar]
            self.abstract_fact = [abstract_fact]

        police_grammar = """
            S -> ADVP COMMA S3 [1.0]
            
            ADVP -> ARB [1.0]
            COMMA -> ',' [1.0]
            CC -> 'and' [1.0]
            S3 -> S4 CC S5 [1.0]
            
            ARB -> '"Unfortunately' [1.0]
            S4 -> NP2 VP2 [1.0]
            S5 -> PP COMMA NP3 VP3 [1.0]
            
            NP2 -> NPRP [1.0]
            VP2 -> VVBD2 VNP2 [1.0]
            PP -> PIN PNP [1.0]
            NP3 -> NDT NNN [1.0]
            VP3 -> VVBD3 VNP3 VPP2 [1.0]
            
            NPRP -> 'we' [1.0]
            VVBD2 -> 'had' [1.0]
            VNP2 -> VNP4 VSBAR [1.0]
            PIN -> 'outside' [1.0]
            PNP -> PDT PNN [1.0]
            NDT -> 'the' [1.0]
            NNN -> 'police' [1.0]
            VVBD3 -> 'told' [1.0]
            VNP3 -> VNNP [1.0]
            VPP2 -> VIN2 VNP6 [1.0]
            
           
            VNP4 -> VNNS [1.0]
            VSBAR -> VWHNP S6 [1.0]
            PDT -> 'the' [1.0]
            PNN -> 'structure"' [1.0]
            VNNP -> 'CNN' [1.0]
            VIN2 -> 'on' [1.0]
            VNP6 -> VNNP2 [1.0]
            
            VNNS -> 'shootings' [1.0]
            VWHNP -> VWDT [1.0]
            S6 -> VP4 [1.0]
            VNNP2 -> 'Monday' [1.0]
            
            VWDT -> 'that' [1.0]
            VP4 -> VVBD4 VADVP [1.0]
            
            VVBD4 -> 'occurred' [1.0]
            VADVP -> VRB [1.0]
            VRB -> 'inside' [1.0]
        """

        # "unfortunately, we had shootings that occurred inside and outside the structure", the police told CNN on Monday.
        police_fact_tree = Fact(
            subj=Person(kind=self.morphy('police', 'noun')),
            event=Event(kind=self.morphy('told', 'verb'),
                        attrs={'day': 'Monday',
                               'clause_mod': Clause(connective='that',
                                                    subj=Person(kind='we'),
                                                    event=Event(kind=self.morphy('had', 'verb')),
                                                    obj=Object(kind=self.morphy('shootings', 'noun'),
                                                               attrs={'clause_rel': Fact(
                                                                   subj=Object(kind=self.morphy('shootings', 'noun')),
                                                                   event=Event(kind=self.morphy('occurred', 'verb'),
                                                                               attrs={
                                                                                   'phrase_mod': Multiple(conj='and',
                                                                                                          nodes=[Phrase(
                                                                                                              kind='inside',
                                                                                                              attrs={
                                                                                                                  'obj': 'structure'}),
                                                                                                              Phrase(
                                                                                                                  kind='outside',
                                                                                                                  attrs={
                                                                                                                      'obj': 'structure'})])
                                                                               }))}))}),
            obj=Object(kind='CNN')
        )

        if event == 'shooting':
            self.grammar += [police_grammar]
            self.abstract_fact += [police_fact_tree]

        # "We're trying to piece everything together."
        police_grammar_2 = """
            S -> NP VP [1.0]
            NP -> NPRP [1.0]
            VP -> VVBP VP2 [1.0]
            
            VVBP -> 'are' [1.0]
            VP2 -> VVBG VPP VADVP [1.0]
            NPRP -> '"We' [1.0]
            VVBG -> 'trying' [1.0]
            VPP -> VIN VNP [1.0]
            VADVP -> VRB [1.0]
            
            VIN -> 'to' [1.0]
            VNP -> VNN VNN2 [1.0]
            VRB -> 'together."' [1.0]
            VNN -> 'piece' [1.0]
            VNN2 -> 'everything' [1.0]
        """

        abstract_fact_2 = Fact(
            subj=Person(kind='we'),
            event=Event(kind=self.morphy('trying', 'verb'),
                        attrs={'phrase_mod': Phrase(kind='to',
                                                    attrs={'event': Event(kind=self.morphy('piece', 'verb'),
                                                                          attrs={'obj': 'everything',
                                                                                 'event_mod': 'together'})})})
        )

        police_grammar_3 = """
            S -> NP VP [1.0]
            NP -> NNNS [1.0]
            VP -> VVBP VVP [1.0]
            
            NNNS -> 'police' [1.0]
            VVBP -> 'are' [1.0]
            VVP -> VVBG VPP S2 [1.0]
            
            VVBG -> 'asking' [1.0]
            VPP -> VIN VNP [1.0]
            S2 -> VP2 [1.0]
            
            VIN -> 'for' [1.0]
            VNP -> VNP2 VPP2 [1.0]
            VP2 -> VTO VVP2 [1.0]
            
            VNP2 -> VDT VNN [1.0]
            VPP2 -> VIN2 VNP3 [1.0]
            VTO -> 'to' [1.0]
            VVP2 -> VVP3 CC VVP4 [1.0]
            
            VDT -> 'the' [1.0]
            VNN -> 'cooperation' [1.0]
            VIN2 -> 'of' [1.0]
            VNP3 -> VDT VNN2 [1.0]
            VVP3 -> VVB VADVP [1.0]
            CC -> 'and' [1.0]
            VVP4 -> VVB2 VNP4 VPP3 [1.0]
            
            VNN2 -> 'public' [1.0]
            VVB -> 'come' [1.0]
            VADVP -> VRB [1.0]
            VVB2 -> 'help' [1.0]
            VNP4 -> VPRP [1.0]
            VPP3 -> VIN3 VNP5 [1.0]
            
            VRB -> 'forward' [1.0]
            VPRP -> 'us' [1.0]
            VIN3 -> 'with' [1.0]
            VNP5 -> VDT VNN3 [1.0]
            VNN3 -> 'investigation' [1.0]
        """

        # Police are asking for the cooperation of the public to come forward and help us with the investigation.
        abstract_fact_3 = Fact(
            subj=Object(kind=self.morphy('police', 'noun')),
            event=Event(kind=self.morphy('asking', 'verb'),
                        attrs={'phrase_mod_1': Phrase(kind='for',
                                                      attrs={'obj': Object(kind=self.morphy('cooperation', 'noun'),
                                                                           attrs={'phrase_mod': Phrase('of', attrs={
                                                                               'obj': 'public'})})}),
                               'phrase_mod_2': Phrase(kind='to',
                                                      attrs={'event': Multiple(conj='and',
                                                                               nodes=[Event(
                                                                                   kind=self.morphy('come', 'verb'),
                                                                                   attrs={'event_mod': 'forward'}),
                                                                                      Event(kind=self.morphy('help',
                                                                                                             'verb'),
                                                                                            attrs={'obj': 'us',
                                                                                                   'phrase_mod': Phrase(
                                                                                                       kind='with',
                                                                                                       attrs={
                                                                                                           'obj': 'investigation'})})])})})
        )

        police_grammar_4 = """
            S -> NP VP [1.0]
            NP -> NNP NADVP [1.0]
            VP -> VVBD S2 [1.0]
            
            NNP -> NDT NNN NNN2 [1.0]
            NADVP -> NRBR [1.0]
            VVBD -> 'called' [1.0]
            S2 -> NP2 ADJP [1.0]
            
            NDT -> 'the' [1.0]
            NNN -> 'police' [1.0]
            NNN2 -> 'chief' [1.0]
            NRBR -> 'earlier' [1.0]
            NP2 -> NDT NNN3 [1.0]
            ADJP -> AJJ [1.0]
            
            NNN3 -> 'incident' [1.0]
            AJJ -> 'heartbreaking' [1.0]
        """

        abstract_fact_4 = Fact(
            subj=Person(kind=self.morphy('chief', 'noun'), attrs={'obj_mod': 'police'}),
            event=Event(kind=self.morphy('called', 'verb')),
            obj=Object(kind=self.morphy('incident', 'noun'), attrs={'obj_mod': 'heartbreaking'})
        )

        # Investigators are collecting evidence from the crime scene, officials said
        police_grammar_5 = """
            S -> PRN COMMA NP VP [1.0]
            PRN -> S2 [1.0]
            COMMA -> ',' [1.0]
            NP -> NNNS [1.0]
            VP -> VVBD [1.0]
            
            S2 -> NP2 VP2 [1.0]
            NNNS -> 'officials' [1.0]
            VVBD -> 'said' [1.0]
            
            NP2 -> NNNS2 [1.0]
            VP2 -> VVBP VVP [1.0]
            
            NNNS2 -> 'investigators' [1.0]
            VVBP -> 'are' [1.0]
            VVP -> VVBG VNP VPP [1.0]
            
            VVBG -> 'collecting' [1.0]
            VNP -> VNN [1.0]
            VPP -> VIN VNP2 [1.0]
            
            VNN -> 'evidence' [1.0]
            VIN -> 'from' [1.0]
            VNP2 -> VDT VNN2 VNN3 [1.0]
            
            VDT -> 'the' [1.0]
            VNN2 -> 'crime' [1.0]
            VNN3 -> 'scene' [1.0]
        """

        abstract_fact_5 = Fact(
            subj=Person(kind=self.morphy('officials', 'noun')),
            event=Event(kind=self.morphy('said', 'verb')),
            obj=Fact(
                subj=Person(kind=self.morphy('investigators', 'noun')),
                event=Event(kind=self.morphy('collecting', 'verb')),
                obj=Object(kind=self.morphy('evidence', 'noun'), attrs={
                    'phrase_mod': Phrase(kind='from', attrs={'obj': Object(kind='scene', attrs={'obj_mod': 'crime'})})})
            )
        )

        self.grammar += [police_grammar_2, police_grammar_3, police_grammar_4, police_grammar_5]
        self.abstract_fact += [abstract_fact_2, abstract_fact_3, abstract_fact_4, abstract_fact_5]
