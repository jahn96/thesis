from Attributes.AgeAttribute import AgeAttribute
from Attributes.Attribute import Attribute
from Attributes.DayAttribute import DayAttribute
from Attributes.LocationAttribute import LocationAttribute
from Attributes.NationalityAttribute import NationalityAttribute
from Attributes.SexAttribute import SexAttribute
from Attributes.TimeAttribute import TimeAttribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class EventHeadLineGrammar(Grammar):
    """
    Grammar that shows the headline of the crime event in an article
    """
    def __init__(self, tense: str, grammar_type: int, num_criminals: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)
        self.__num_criminals = num_criminals

    def define_grammar(self):
        # TODO: plural (if count is one, then noun should be singular)
        # NOTE: (verb and object) should be something that comes together such as 'break into a bank' :)
        # TODO: Consider generating (count + noun) such as three men

        # TODO: change grammar type to better id (it doesn't have to be int)!
        if self.grammar_type == 1:
            crime_event_grammar = """
                S -> NP VP              [1.0]
                NP -> NDT NAGE NSEX NNN [1.0]
                NAGE -> '[AGE]' [1.0]
                NDT -> 'A' [1.0]
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
            
                VCD -> '{self.__num_criminals}' [1.0]
                VNNS -> 'men' [1.0]
                VDT -> 'a' [1.0]
                VNN -> '[OBJ_MOD]' [1.0]
                VNN2 -> 'restaurant' [1.0]
                VIN5 -> 'in' [1.0]
                VNP6 -> VNN3 [1.0]
    
                VNN3 -> '[LOCATION]' [1.0]
            """

            # A 13-year old female victim got knifepointed by 3 men at a steak restaurant in madrid at 7:26 a.m. on Monday.
            verb = self.stemmer.stem(self.metadata['event'])
            abstract_fact = Fact(obj=Person(kind='men', attrs={'count': self.__num_criminals}),
                                 event=Event(kind=verb, passive=True, attrs={
                                     'subj': 'victim',
                                     'obj': 'men',
                                     'day': DayAttribute(),
                                     'time': TimeAttribute(),
                                     'place': Object(kind='restaurant',
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
            crime_event_grammar = """
                S -> NP VP [1.0]
                
                NP -> NDT NNATIONALITY NNN [1.0]
                NDT -> 'A' [1.0]
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

            crime_event_grammar += """
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
            VJJ -> 'stabbing' [1.0]
            VNN -> 'death' [1.0]
            VIN5 -> 'of' [1.0]
            VNP8 -> VDT2 VNATIONALITY VNN5 [1.0]
            VDT2 -> 'a' [1.0]
            VNN2 -> 'nightclub brawl' [1.0]
            VLOC -> '[LOCATION]' [1.0]
            
            VNN4 -> 'prison' [1.0]
            VNATIONALITY -> '[NATIONALITY]' [1.0]
            VNN5 -> 'soldier' [1.0]
            """

            # A Spanish tourist had been sentenced to 10 years in prison over the stabbing death of a Nigerian soldier during a nightclub brawl in the United States
            abstract_fact = Fact(
                subj=Person(kind='tourist', attrs={'nationality': NationalityAttribute()}),
                event=Event(kind=self.stemmer.stem('sentenced'),
                            passive=True,
                            attrs={'subj': 'tourist',
                                   'phrase_mod': [Phrase(kind='to', attrs={'obj': Object(kind='years',
                                                                                         attrs={'count': 10,
                                                                                                'place': 'prison'})}),
                                                  Phrase(kind='over', attrs={'obj': Object(kind='death',
                                                                                           attrs={
                                                                                               'obj_mod': 'stabbing',
                                                                                               'phrase_mod': Phrase(
                                                                                                   kind='of',
                                                                                                   attrs={'obj': Person(
                                                                                                       kind='soldier',
                                                                                                       attrs={
                                                                                                           'nationality': NationalityAttribute()})})})}),
                                                  Phrase(kind='during', attrs={'obj': Object(kind='nightclub brawl',
                                                                                             attrs={
                                                                                                 'location': LocationAttribute(),
                                                                                             })})]})
            )

            self.grammar = crime_event_grammar
            self.abstract_fact = abstract_fact

#
#
#
#         crime_grammar_2 = """
#       S -> NP COMMA S2 COMMA VP [1.0]
#
#       NP -> NNAME [1.0]
#       COMMA -> ',' [1.0]
#       S2 -> UCP [1.0]
#       """
#
#         if self.tense == 'present':
#             crime_grammar_2 += """
#         VP -> VVBZ2 VVP [1.0]
#         VVBZ2 -> 'is' [1.0]
#       """
#
#         else:
#             crime_grammar_2 += """
#         VP -> VVBD2 VVP [1.0]
#         VVBD2 -> 'was' [1.0]
#       """
#
#         crime_grammar_2 += """
#       NNAME -> '[NAME]' [1.0]
#       UCP -> UPP COMMA UCC S3 [1.0]
#       VVP -> VVBN VCC VVBN2 VNP [1.0]
#
#       UPP -> UADVP UIN UNATIONALITY [1.0]
#       UCC -> 'but' [1.0]
#       S3 -> VP2 [1.0]
#       VVBN -> 'provoked' [1.0]
#       VCC -> 'and' [1.0]
#       VVBN2 -> 'lost' [1.0]
#       VNP -> VNP2 [0.5] | VNP2 VSBAR2 [0.5]
#
#       UADVP -> URB [1.0]
#       UIN -> 'from' [1.0]
#       UNATIONALITY -> '[NATIONALITY]' [1.0]
#       VP2 -> VBG VPP [1.0]
#       VNP2 -> VNN HYPH VNN2 [1.0]
#       VSBAR2 -> VWHADVP S4 [1.0]
#
#       URB -> 'originally' [1.0]
#       VBG -> 'living' [1.0]
#       VPP -> VIN2 VCITY [1.0]
#       VNN -> 'self' [1.0]
#       HYPH -> '-' [1.0]
#       VNN2 -> 'control' [1.0]
#       VWHADVP -> VWRB [1.0]
#       S4 -> NP2 VP3 [1.0]
#
#       VIN2 -> 'in' [1.0]
#       VCITY -> '[CITY]' [1.0]
#       VWRB -> 'when' [1.0]
#       NP2 -> NPRP [1.0]
#       VP3 -> VVP2 VCC VADVP VVP3 [1.0]
#       """
#
#         if self.tense == 'present':
#             crime_grammar_2 += """
#         VVP2 -> VVBZ3 VPRT VNP3 [1.0]
#         VVP3 -> VVBZ4 VNAME [1.0]
#         VVBZ3 -> 'pulled' [1.0]
#         VVBZ4 -> 'stabbed' [1.0]
#       """
#         else:
#             crime_grammar_2 += """
#         VVP2 -> VVBD3 VPRT VNP3 [1.0]
#         VVP3 -> VVBD4 VNAME [1.0]
#         VVBD3 -> 'pulled' [1.0]
#         VVBD4 -> 'stabbed' [1.0]
#       """
#         crime_grammar_2 += """
#       NPRP -> 'he' [1.0]
#       VADVP -> VRB [1.0]
#
#       VPRT -> VRP [1.0]
#       VNP3 -> VDT VNN3 [1.0]
#       VRB -> 'fatally' [1.0]
#       VNAME -> '[NAME]' [1.0]
#
#       VRP -> 'out' [1.0]
#       VDT -> 'a' [1.0]
#       VNN3 -> 'switchblade' [1.0]
#     """
#
#         crime_grammar_3 = """
#       S -> NP VP [1.0]
#
#       NP -> NNP NPP [1.0]
#
#       NNP -> NNP2 NNN NNN2 [1.0]
#       NPP -> NIN NNP3 [1.0]
#
#       NNP2 -> NNAME NPOS [1.0]
#       NNN -> 'hotel' [1.0]
#       NNN2 -> 'room' [1.0]
#       NIN -> 'at' [1.0]
#       NNP3 -> NDT NNN3 [1.0]
#
#       NNAME -> '[NAME]' [1.0]
#       NPOS -> "'s" [1.0]
#       NDT -> 'the' [1.0]
#       NNN3 -> 'time' [1.0]"""
#
#         if self.tense == 'present':
#             crime_grammar_3 += """
#         VP -> VVBZ VPRT VNP [0.5] | VVBZ VPRT VNP VSBAR [0.5]
#         VVBD -> 'turns' [1.0]
#       """
#         else:
#             crime_grammar_3 += """
#         VP -> VVBD VPRT VNP [0.5] | VVBD VPRT VNP VSBAR [0.5]
#         VVBD -> 'turned' [1.0]
#       """
#
#         crime_grammar_3 += """
#       VPRT -> VRP [1.0]
#       VNP -> VNP2 COMMA VNP3 COMMA VCC VNP4 [1.0]
#       VSBAR -> VIN S2 [1.0]
#
#       VRP -> 'up' [1.0]
#       VNP2 -> VNN [1.0]
#       COMMA -> ',' [1.0]
#       VNP3 -> VCD VNN2 VNNS [1.0]
#       VCC -> 'and' [1.0]
#       VNP4 -> VCD2 VNNS2 [1.0]
#       VIN -> 'that' [1.0]
#       S2 -> NP2 VP2 [1.0]
#
#       VNN -> 'marijuana' [1.0]
#       VCD -> '[COUNT]' [1.0]
#       VNN2 -> 'brass' [1.0]
#       VNNS -> 'knuckles' [1.0]
#       VCD2 -> '[COUNT]' [1.0]
#       VNNS2 -> 'switchblades' [1.0]
#       NP2 -> NPRP [1.0]
#     """
#
#         if self.tense == 'present':
#             crime_grammar_3 += """
#         VP2 -> VVBZ2 VPP [1.0]
#         VVBZ2 -> 'buys' [1.0]
#       """
#         else:
#             crime_grammar_3 += """
#         VP2 -> VVBD2 VPP [1.0]
#         VVBD2 -> 'bought' [1.0]
#       """
#
#         crime_grammar_3 += """
#       NPRP -> 'he' [1.0]
#       VPP -> VIN2 VNP5 [1.0]
#
#       VIN2 -> 'as' [1.0]
#       VNP5 -> VNNS3 [1.0]
#       VNNS3 -> 'souvenirs' [1.0]
#     """
#
#         num_soldiers = random.choice(range(1, num_facts))
#         num_tourists = num_facts - num_soldiers
#
#         crime_grammar_4 = """
#       S -> NP VP [1.0]
#
#       NP -> NDT NNN [1.0]
#       NDT -> 'The' [1.0]
#       NNN -> 'stabbing' [1.0]
#       """
#         if self.tense == 'present':
#             crime_grammar_4 += """
#         VP -> VVBZ VNP VPP VPP2 [1.0]
#         VVBZ -> 'takes' [1.0]
#       """
#         else:
#             crime_grammar_4 += """
#         VP -> VVBD VNP VPP VPP2 [1.0]
#         VVBD -> 'took' [1.0]
#       """
#
#         crime_grammar_4 += """
#       VNP -> VNN [1.0]
#       VPP -> VIN VNP2 [1.0]
#       VPP2 -> VIN2 VNP3 [1.0]
#
#       VNN -> 'place' [1.0]
#       VIN -> 'during' [1.0]
#       VNP2 -> VNP4 VPP3 [1.0]
#       VIN2 -> 'at' [1.0]
#       VNP3 -> VDT VNN2 [1.0]
#
#       VNP4 -> VDT2 VNN3 [1.0]
#       VPP3 -> VIN3 VNP5 [1.0]
#       VDT -> 'this' [1.0]
#       VNN2 -> 'nightclub' [1.0]
#
#       VDT2 -> 'a' [1.0]
#       VNN3 -> 'fight' [1.0]
#       VIN3 -> 'between' [1.0]
#       VNP5 -> VNP6 VCC VNP7 [1.0]
#       """
#
#         if num_soldiers < 2:
#             crime_grammar_4 += """
#           VNP6 -> VCD1 VNATIONALITY VNN4 [1.0]
#           VNN4 -> 'soldier' [1.0]
#       """
#         else:
#             crime_grammar_4 += """
#         VNP6 -> VCD1 VNATIONALITY VNNS [1.0]
#         VNNS -> 'soldiers' [1.0]
#       """
#
#         if num_tourists < 2:
#             crime_grammar_4 += """
#         VNP7 -> VCD2 VNATIONALITY VNN5 [1.0]
#         VNN5 -> 'tourist' [1.0]
#       """
#         else:
#             crime_grammar_4 += """
#         VNP7 -> VCD2 VNATIONALITY VNNS2 [1.0]
#         VNNS2 -> 'tourists' [1.0]
#       """
#         crime_grammar_4 += f"""
#       VCC -> 'and' [1.0]
#
#       VCD1 -> '{num_soldiers}' [1.0]
#       VNATIONALITY -> '[NATIONALITY]' [1.0]
#       VCD2 -> '{num_tourists}' [1.0]
#     """
#
#         grammars = {
#             'non_desc': [crime_head_grammar, crime_grammar_1, crime_grammar_2, crime_grammar_3, crime_grammar_4]}
#
#         crime_desc_grammar_obj = CrimeCriminalDescriptionGrammar(self.tense, nouns='soldiers')
#         soldier_desc_grammars = crime_desc_grammar_obj.define_grammar()
#
#         grammars['desc'] = [{'soldier': soldier_desc_grammars, 'num_facts': num_soldiers}]
#
#         crime_desc_grammar_obj_2 = CrimeCriminalDescriptionGrammar(self.tense, nouns='tourists')
#         tourist_desc_grammars = crime_desc_grammar_obj_2.define_grammar()
#
#         grammars['desc'].append({'tourist': tourist_desc_grammars, 'num_facts': num_tourists})
#
#         return grammars
