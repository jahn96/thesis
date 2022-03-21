from Attributes.Attribute import Attribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from generator.Grammar.Grammar import Grammar


# TODO: add condolence from police
"""
"Our thoughts and prayers are with his family and also with all the families and our shooting victims as a result of this incident," Col. Bill Bryant of the Arkansas State Police told reporters.
"""

class PoliceReportGrammar(Grammar):
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def get_next_day(self, date):
        if date.lower() == 'monday':
            return 'Tuesday'
        elif date.lower() == 'tuesday':
            return 'Wednesday'
        elif date.lower() == 'wednesday':
            return 'Thursday'
        elif date.lower() == 'thursday':
            return 'Friday'
        elif date.lower() == 'friday':
            return 'Saturday'
        elif date.lower() == 'saturday':
            return 'Sunday'
        elif date.lower() == 'sunday':
            return 'Monday'

    def define_grammar(self):
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

            next_day = self.get_next_day(day)

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
                
                NDT -> 'a' [1.0]
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
                VNNP2 -> '{next_day}' [1.0]
                
                VNP3 -> VDT VJJ2 VNN2 [1.0]
                VPP3 -> VIN3 VNP4 [1.0]
                VNN -> 'custody' [1.0]
                
                VDT -> 'a' [1.0]
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
                                 event=Event(kind=self.stemmer.stem('said'), attrs={'subj': 'police'}),
                                 obj=Fact(
                                     subj=Person(kind='man',
                                                 attrs={
                                                     'clause_mod': Fact(event=Event(kind=self.stemmer.stem('suspected'),
                                                                                    attrs={'subj': 'man',
                                                                                           'phrase_mod':
                                                                                               Object(kind='in',
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
                                         kind=self.stemmer.stem('taken'),
                                         passive=True,
                                         attrs={
                                             'phrase_mod': Object(kind='into', attrs={'obj': 'custody'}),
                                             'subj': 'man',
                                             'day': next_day})))

            self.grammar = police_report_grammar
            self.abstract_fact = abstract_fact

        elif self.grammar_type == 2:
            grammar = """
                S -> QUOTE S2 COMMA QUOTE NP VP [1.0]
                
                QUOTE -> '"' [1.0]
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
                
                NDT -> 'The' [1.0]
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
                VVBN -> 'determined' [1.0]
                
                VVBD2 -> 'led' [1.0]
                VPRT -> VRP [1.0]
                VPP -> VIN VNP [1.0]
                
                VRP -> 'up' [1.0]
                VIN -> 'to' [1.0]
                VNP -> VDT VNN [1.0]
                VDT -> 'this' [1.0]
                VNN -> 'stabbing' [1.0]
            """

            # TODO: NOTE: Event should have subj/obj attribute
            # "The facts and circumstances that led up to this shooting are still (being) determined," police said.
            abstract_fact = Fact(subj=Person(kind='police'),
                                 event=Event(kind=self.stemmer.stem('said'), attrs={'subj': 'police'}),
                                 obj=Fact(
                                     subj=[Object(kind='fact', attrs={'clause_mod':
                                         Fact(
                                             event=Event(kind=self.stemmer.stem('led up'),
                                                         attrs={'subj': 'fact',
                                                                'phrase_mod': Object(kind='to',
                                                                                     attrs={
                                                                                         'obj': 'stabbing'})}))
                                     }), Object(kind='circumstances', attrs={'clause_mod':
                                         Fact(
                                             event=Event(kind=self.stemmer.stem('led up'),
                                                         attrs={'subj': 'circumstance',
                                                                'phrase_mod': Object(kind='to',
                                                                                     attrs={
                                                                                         'obj': 'stabbing'})}))
                                     })],
                                     event=Event(kind=self.stemmer.stem('determined'),
                                                 passive=True,
                                                 attrs={'subj': 'fact, circumstance', 'event_mod': 'still'}))
                                 )
            self.grammar = grammar
            self.abstract_fact = abstract_fact
