from Attributes.AgeAttribute import AgeAttribute
from Attributes.Attribute import Attribute
from Attributes.DayAttribute import DayAttribute
from Attributes.LocationAttribute import LocationAttribute
from Attributes.NationalityAttribute import NationalityAttribute
from Attributes.SexAttribute import SexAttribute
from Attributes.TimeAttribute import TimeAttribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class EventHeadLineGrammar(Grammar):
    """
    Grammar that shows the headline of the crime event in an article
    """
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        # TODO: plural (if count is one, then noun should be singular)
        # NOTE: (verb and object) should be something that comes together such as 'break into a bank' :)
        # TODO: Consider generating (count + noun) such as three men

        # TODO: change grammar type to better id (it doesn't have to be int)!
        if self.grammar_type == 1:
            if 'num_criminals' not in self.metadata:
                print('Please specify num_criminals as a metadata for event headline grammar')
                exit(-1)

            num_criminals = self.metadata['num_criminals']
            event_place = self.metadata['place']

            crime_event_grammar = """
                S -> NP VP              [1.0]
                NP -> NDT NAGE NSEX NNN [1.0]
                NAGE -> '[AGE]' [1.0]
                NDT -> '[ARTICLE]' [1.0]
                NSEX -> '[SEX]' [1.0]
                NNN -> 'victim' [1.0]
            """

            if self.tense == 'present':
                crime_event_grammar += """
                    VP -> VVBZ VADJP VPP VPP2 VPP3 [1.0]
                    VVBZ -> 'gets' [1.0]
                """
            else:
                crime_event_grammar += """
                    VP -> VVBD VADJP VPP VPP2 VPP3 [1.0]
                    VVBD -> 'got' [1.0]
                """

            crime_event_grammar += f"""
                VADJP -> VJJ VPP4 [1.0]
                VPP -> VIN VNP [1.0]
                VPP2 -> VIN2 VNP2 [1.0]
                VPP3 -> VIN3 VNP3 [1.0]
    
                VJJ -> '{self.metadata['event']}' [1.0]
                VPP4 -> VIN4 VNP4 [1.0]
                VIN -> 'at' [1.0]
                VNP -> VNP5 VPP5 [1.0]
                VIN2 -> 'at' [1.0]
                VNP2 -> VTMP [1.0]
                VIN3 -> 'on' [1.0]
                VNP3 -> VNNP [1.0]
    
                VIN4 -> 'by' [1.0]
                VNP4 -> VCD VNNS [1.0]
                VNP5 -> VDT VNN VNN2 [1.0]
                VPP5 -> VIN5 VNP6 [1.0]
                VTMP -> '[TIME]' [1.0]
                VNNP -> '[DAY]' [1.0]
            
                VCD -> '{num_criminals}' [1.0]
                VNNS -> 'men' [1.0]
                VDT -> '[ARTICLE]' [1.0]
                VNN -> '[OBJ_MOD]' [1.0]
                VNN2 -> '{event_place}' [1.0]
                VIN5 -> 'in' [1.0]
                VNP6 -> VNN3 [1.0]
    
                VNN3 -> '[LOCATION]' [1.0]
            """

            # A 13-year old female victim got knifepointed by 3 men at a steak restaurant in madrid at 7:26 a.m. on Monday.
            verb = self.morphy(self.metadata['event'], 'verb')
            abstract_fact = Fact(obj=Person(kind='men', attrs={'count': str(num_criminals)}),
                                 event=Event(kind=verb, passive=True, attrs={
                                     # TODO: check to see if subject and object work without having them passed as attributes
                                     'subj': 'victim',
                                     'obj': 'men',
                                     'day': DayAttribute(),
                                     'time': TimeAttribute(),
                                     'place': Object(kind=event_place,
                                                     attrs={
                                                         'obj_mod': Attribute(),
                                                         'location': LocationAttribute()
                                                     }),
                                     # 'phrase_mod': [
                                     #     Object(kind='at', attrs={
                                     #         'obj': Object(kind='restaurant',
                                     #                       attrs={
                                     #                           'obj_mod': Attribute(),
                                     #                           'phrase_mod': Object(
                                     #                               kind='at',
                                     #                               attrs={
                                     #                                   'obj': LocationAttribute()})
                                     #                       })})
                                     # ],
                                 }),
                                 subj=Person(kind='victim', attrs={'sex': SexAttribute(), 'age': AgeAttribute()}))
            self.grammar = crime_event_grammar
            self.abstract_fact = abstract_fact

        elif self.grammar_type == 2:
            if not self.metadata:
                print('Event must be passed as a metadata!')
                exit(-1)

            if 'event' not in self.metadata:
                print('Event must be passed as a metadata!')
                exit(-1)

            event = self.metadata['event']

            crime_event_grammar = """
                S -> NP VP [1.0]
                
                NP -> NDT NNATIONALITY NNN [1.0]
                NDT -> '[ARTICLE]' [1.0]
                NNATIONALITY -> '[NATIONALITY]' [1.0]
                NNN -> 'tourist' [1.0]
                """

            if self.tense == 'present':
                crime_event_grammar += """
                VP -> VVBZ VVP [1.0]
                VVBZ -> 'has' [1.0]
                """
            else:
                crime_event_grammar += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'had' [1.0]
                """

            crime_event_grammar += f"""
            VVP -> VVBN VVP2 [1.0]
            VVBN -> 'been' [1.0]
            
            VVP2 -> VVBN2 VPP VPP2 VPP3 [1.0]
            VVBN2 -> 'sentenced' [1.0]
            VPP -> VIN VNP [1.0]
            VPP2 -> VIN2 VNP2 [1.0]
            VPP3 -> VIN3 VNP3 [1.0]
            
            VIN -> 'to' [1.0]
            VNP -> VPERIOD VPP4 [1.0]
            VIN2 -> 'over' [1.0]
            VNP2 -> VNP5 VPP5 [1.0]
            VIN3 -> 'during' [1.0]
            VNP3 -> VNP6 VPP6 [1.0]
            
            VPERIOD -> VCD VNNS [1.0]
            VCD -> '10' [1.0]
            VNNS -> 'years' [1.0]
            VPP4 -> VIN4 VNP7 [1.0]
            VNP5 -> VDT VJJ VNN [1.0]
            VPP5 -> VIN5 VNP8 [1.0]
            VNP6 -> VDT2 VNN2 [1.0]
            VPP6 -> VIN4 VLOC [1.0]
            
            VIN4 -> 'in' [1.0]
            VNP7 -> VNN4 [1.0]
            VDT -> 'the' [1.0]
            VJJ -> '{event}' [1.0]
            VNN -> 'death' [1.0]
            VIN5 -> 'of' [1.0]
            VNP8 -> VDT2 VNATIONALITY VNN5 [1.0]
            VDT2 -> '[ARTICLE]' [1.0]
            VNN2 -> 'nightclub brawl' [1.0]
            VLOC -> '[LOCATION]' [1.0]
            
            VNN4 -> 'prison' [1.0]
            VNATIONALITY -> '[NATIONALITY]' [1.0]
            VNN5 -> 'soldier' [1.0]
            """

            # A Spanish tourist had been sentenced to 10 years in prison over the stabbing death of a Nigerian soldier during a nightclub brawl in the United States
            abstract_fact = Fact(
                subj=Person(kind='tourist', attrs={'nationality': NationalityAttribute()}),
                event=Event(kind=self.morphy('sentenced', 'verb'),
                            passive=True,
                            attrs={'subj': 'tourist',
                                   'phrase_mod': Multiple(conj='', nodes=[Phrase(kind='to', attrs={'obj': Object(kind='years',
                                                                                         attrs={'count': '10',
                                                                                                'place': 'prison'})}),
                                                  Phrase(kind='over', attrs={'obj': Object(kind='death',
                                                                                           attrs={
                                                                                               'obj_mod': event,
                                                                                               'phrase_mod': Phrase(
                                                                                                   kind='of',
                                                                                                   attrs={'obj': Person(
                                                                                                       kind='soldier',
                                                                                                       attrs={
                                                                                                           'nationality': NationalityAttribute()})})})}),
                                                  Phrase(kind='during', attrs={'obj': Object(kind='brawl',
                                                                                             attrs={
                                                                                                 'obj_mod': 'nightclub',
                                                                                                 'location': LocationAttribute(),
                                                                                             })})])})
            )

            self.grammar = crime_event_grammar
            self.abstract_fact = abstract_fact

        elif self.grammar_type == 3:
            num_killed = self.metadata['num_killed']
            num_injured = self.metadata['num_injured']
            event = self.metadata['event']
            #   One person was killed and four others were injured in the shooting.
            crime_event_grammar = f"""
            S -> S1 CC S2 [1.0]
            
            S1 -> NP VP [1.0]
            NP -> NCD NNN [1.0]
            NCD -> '{num_killed}' [1.0]
            NNN -> 'person' [1.0]
            
            VP -> VVBD VVP [1.0]
            VVBD -> 'was' [1.0]
            VVP -> VVBN [1.0]
            VVBN -> 'killed' [1.0]
            
            CC -> 'and' [1.0]
            
            S2 -> NP2 VP2 [1.0]
            NP2 -> NCD2 NNNS [1.0]
            NCD2 -> '{num_injured}' [1.0]
            NNNS -> 'people' [1.0]
            VP2 -> VVBD2 VVP2 [1.0]
            VVBD2 -> 'were' [1.0]
            VVP2 -> VVBN2 VPP [1.0]
            VVBN2 -> 'injured' [1.0]
            VPP -> VIN VNP [1.0]
            VIN -> 'in' [1.0]
            VNP -> VDT VNN [1.0]
            
            VDT -> 'the' [1.0]
            VNN -> '{event}' [1.0]
            """

            # TODO: make it to the list of fact
            abstract_fact = Multiple(conj='and', nodes=[Fact(
                subj=Person(kind=self.morphy('person', 'noun'), attrs={'count': 'one'}),
                event=Event(kind=self.morphy('killed', 'verb'), passive=True, attrs={'event': Object(kind=event)})
            ), Fact(
                subj=Person(kind=self.morphy('people', 'noun'), attrs={'count': 'four'}),
                event=Event(kind=self.morphy('injured', 'verb'), passive=True, attrs={'event': Object(kind=event)})
            )])

            self.grammar = crime_event_grammar
            self.abstract_fact = abstract_fact
