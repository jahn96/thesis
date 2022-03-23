from Attributes.AgeAttribute import AgeAttribute
from Attributes.Attribute import Attribute
from Attributes.MonthAttribute import MonthAttribute
from Attributes.NameAttribute import NameAttribute
from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class SceneDescriptionGrammar(Grammar):
    """
    Grammar that describes the scene where the event was happened
    """

    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        # if not self.metadata:
        #     print('Please provide metadata that contains which event this grammar should describe!')
        #     exit(-1)
        #
        # if 'event_kind' not in self.metadata:
        #     print('Please provide which event this grammar should describe!')
        #     exit(-1)

        # this should be same as the location in the previous sentence
        location = 'london'
        # TODO: city should be from the nation

        if self.grammar_type == 2:
            crime_scene_grammar = """
            S -> NP VP [1.0]
            
            NP -> NNAME COMMA NAGE COMMA [1.0]
            NNAME -> '[NAME]' [1.0]
            COMMA -> ',' [1.0]
            NAGE -> '[AGE]' [1.0]
            """

            if self.tense == 'present':
                crime_scene_grammar += """
                VP -> VVBZ VVP [1.0]
                VVBZ -> 'is' [1.0]
                """

            else:
                crime_scene_grammar += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'was' [1.0]
                """

            crime_scene_grammar += f"""
            VVP -> VVBN VPP VSBAR [1.0]
            
            VVBN -> 'stabbed' [1.0]
            VPP -> VIN VNP [1.0]
            VSBAR -> IN S2 [1.0]
            
            VIN -> 'to' [1.0]
            VNP -> VNN [1.0]
            IN -> 'after' [1.0]
            S2 -> NP2 VP2 [1.0]
            VTMP -> VJJ VNNP [1.0]
            
            VNN -> 'death' [1.0]
            NP2 -> NDT NNN [1.0]
            """

            if self.tense == 'present':
                crime_scene_grammar += """
                VP2 -> VVBZ2 VPRT VPP2 VTMP [1.0]
                VVBZ2 -> 'breaks' [1.0]
                """
            else:
                crime_scene_grammar += """
                VP2 -> VVBD2 VPRT VPP2 VTMP [1.0]
                VVBD2 -> 'broke' [1.0]
                """

            crime_scene_grammar += """
            VJJ -> 'last' [1.0]
            VNNP -> '[MONTH]' [1.0]
            
            NDT -> 'a' [1.0]
            NNN -> 'fight' [1.0]
            VPRT -> VRP [1.0]
            VPP2 -> VIN2 VNP2 [1.0]
            
            VRP -> 'out' [1.0]
            VIN2 -> 'in' [1.0]
            VNP2 -> VNP3 VPP3 [1.0]
            
            VNP3 -> VDT VNN2 [1.0]
            VPP3 -> VIN2 VNP4 [1.0]
            
            VDT -> 'a' [1.0]
            VNN2 -> 'nightclub' [1.0]
            VNP4 -> VNP5 [1.0]
            
            VNP5 -> VDT2 VJJ2 VNN3 [1.0]
            
            VDT2 -> 'the' [1.0]
            VJJ2 -> '[OBJ_MOD]' [1.0]
            VNN3 -> 'resort' [1.0]
            """

            abstract_fact = Fact(
                subj=Person(
                    kind='soldier',
                    attrs={
                        'name': NameAttribute(),
                        'age': AgeAttribute(),
                        # 'location': LocationAttribute()  # TODO: should be a city in his nation
                    }
                ),
                event=Event(
                    kind=self.stemmer.stem('stabbed'),
                    passive=True,
                    attrs={
                        'subj': 'soldier',
                        'phrase_mod': Phrase(kind='to', attrs={'obj': 'death'}),
                        'clause_mod': Clause(kind='after',
                                             subj=Object(kind='fight'),
                                             event=Event(kind=self.stemmer.stem(
                                                 'broke out' if self.tense == 'past' else 'breaks out'), attrs={
                                                 'subj': 'fight',
                                                 'place': Object(kind='nightclub',
                                                                 attrs={
                                                                     'place': Object(kind='resort',
                                                                                     attrs={
                                                                                         'obj_mod': Attribute()
                                                                                     })}),
                                                 'month': Object(kind='',
                                                                 attrs={'kind': MonthAttribute(), 'obj_mod': 'last'})
                                             })
                                             )}
                )
            )
            self.grammar = crime_scene_grammar
            self.abstract_fact = abstract_fact
