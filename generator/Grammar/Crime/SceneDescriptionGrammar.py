from Attributes.AgeAttribute import AgeAttribute
from Attributes.Attribute import Attribute
from Attributes.CountAttribute import CountAttribute
from Attributes.MonthAttribute import MonthAttribute
from Attributes.NameAttribute import NameAttribute
from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar

import random


class SceneDescriptionGrammar(Grammar):
    """
    Grammar that describes the scene where the event was happened
    """

    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = ''
        if self.grammar_type == 1:
            if 'place' not in self.metadata:
                print('Please provide the place that the event was happened!')
                exit(-1)

            if 'event' not in self.metadata:
                print('Please provide the event that was happened (ex, stab, shooting, ...)!')
                exit(-1)

            place = self.metadata['place']
            event = self.metadata['event']
            year = str(random.choice(range(1980, 2010)))

            crime_scene_grammar = f"""
                  S -> NP VP [1.0]
                  NP -> NDT NNN [1.0]
                  NDT -> 'the' [1.0]
                  NNN -> '{place}' [1.0]
                """

            if self.tense == 'past':
                crime_scene_grammar += """
                    VP -> VVBD VPP [1.0]
                    VVBD -> 'was' [1.0]
                  """
            else:
                crime_scene_grammar += """
                    VP -> VVBZ VPP [1.0]
                    VVBZ -> 'is' [1.0]
                  """

            crime_scene_grammar += """
                  VPP -> VNP VIN VNP2 [1.0]

                  VNP -> VDT VNN [1.0]
                  VIN -> 'from' [1.0]
                  VNP2 -> VNP3 [1.0]

                  VDT -> '[ARTICLE]' [1.0]
                  VNN -> 'mile' [1.0]
                  VNP3 -> VDT VJJ VADJP VNN2 [1.0]

                  VJJ -> 'memorial' [1.0]
                  VADJP -> VJJ2 VPP2 [1.0]
                  VNN2 -> 'massacre' [1.0]

                  VJJ2 -> 'dedicated' [1.0]
                  VPP2 -> VIN3 VNP4 [1.0]

                  VIN3 -> 'to' [1.0]
                  VNP4 -> VNP5 VSBAR [1.0]

                  VNP5 -> VCD VNNS [1.0]
                  VSBAR -> VWHNP S2 [1.0]

                  VCD -> '[COUNT]' [1.0]
                  VNNS -> 'people' [1.0]
                  VWHNP -> 'who' [1.0]
                  S2 -> VP2 [1.0]
                """

            if self.tense == 'past':
                crime_scene_grammar += """
                    VP2 -> VVBD2 VVP [1.0]
                    VVBD2 -> 'were' [1.0]
                  """
            else:
                crime_scene_grammar += """
                    VP2 -> VVBZ2 VVP [1.0]
                    VVBZ2 -> 'are' [1.0]
                  """

            crime_scene_grammar += f"""
                  VVP -> VVBN VPP3 [1.0]
                  VVBN -> 'killed' [1.0]
                  VPP3 -> VIN4 VNP6 [1.0]

                  VIN4 -> 'in' [1.0]
                  VNP6 -> VDT2 VNNP VCD2 VNN3 [1.0]

                  VDT2 -> '[ARTICLE]' [1.0]
                  VNNP -> '[MONTH]' [1.0]
                  VCD2 -> '{year}' [1.0]
                  VNN3 -> 'shooting' [1.0]
                """
            # The restaurant was a mile from a memorial dedicated to [count] people who were killed in an [month] [year] shooting massacre.
            crime_scene_fact = Fact(
                subj=Object(kind='restaurant', attrs={
                    'dist': Object(kind='mile', attrs={'phrase_mod': Phrase(kind='from',
                                                                            attrs={'obj': Object(kind='memorial',
                                                                                                 attrs={
                                                                                                     'clause_rel': Fact(
                                                                                                         # TODO: combine this with the memorial before
                                                                                                         subj=Object(
                                                                                                             kind='memorial'),
                                                                                                         event=Event(
                                                                                                             kind=self.morphy(
                                                                                                                 'dedicated',
                                                                                                                 'verb'),
                                                                                                             attrs={
                                                                                                                 'phrase_mod': Phrase(
                                                                                                                     kind='to',
                                                                                                                     attrs={
                                                                                                                         'obj': Person(
                                                                                                                             kind='people',
                                                                                                                             attrs={
                                                                                                                                 'count': CountAttribute(),
                                                                                                                                 'clause_rel': Fact(
                                                                                                                                     subj=Object(
                                                                                                                                         kind='people'),
                                                                                                                                     event=Event(
                                                                                                                                         kind=self.morphy(
                                                                                                                                             'killed',
                                                                                                                                             'verb'),
                                                                                                                                         passive=True,
                                                                                                                                         attrs={
                                                                                                                                             'phrase_mod': Phrase(
                                                                                                                                                 kind='in',
                                                                                                                                                 attrs={
                                                                                                                                                     'obj': Object(
                                                                                                                                                         kind='massacre',
                                                                                                                                                         attrs={
                                                                                                                                                             'obj_mod': 'shooting',
                                                                                                                                                             'month': MonthAttribute(),
                                                                                                                                                             'year': year})})})
                                                                                                                                 )})})}
                                                                                                         ))})})
                                                       })})
            )

            next_crime_scene_grammar = f"""
                  S -> NP VP [1.0]
                  NP -> NDT NNN [1.0]

                  NDT -> 'the' [1.0]
                  NNN -> '{place}' [1.0]
                """

            if self.tense == 'past':
                next_crime_scene_grammar += """
                    VP -> VVBD VRB VPP VADVP [1.0]
                    VVBD -> 'was' [1.0]
                  """
            else:
                next_crime_scene_grammar += """
                    VP -> VVBZ VRB VPP VADVP [1.0]
                    VVBZ -> 'is' [1.0]
                  """

            next_crime_scene_grammar += f"""
                  VRB -> 'also' [1.0]
                  VPP -> VIN VNP [1.0]
                  VADVP -> VRB2 VPP2 [1.0]

                  VIN -> 'about' [1.0]
                  VNP -> VDT VNML VNN [1.0]
                  VRB2 -> 'away' [1.0]
                  VPP2 -> VIN2 VSBAR [1.0]

                  VDT -> '[ARTICLE]' [1.0]
                  VNML -> 'half-mile' [1.0]
                  VNN -> 'walk' [1.0]
                  VIN2 -> 'from' [1.0]
                  VSBAR -> VWHADVP S2 [1.0]

                  VWHADVP -> VWRB [1.0]
                  S2 -> NP2 VP2 [1.0]

                  VWRB -> 'where' [1.0]
                  NP2 -> NNP NPP [1.0]
                  VP2 -> VVBD2 VVP [1.0]

                  NNP -> NJJS [1.0]
                  NPP -> NIN NNP2 [1.0]
                  VVBD2 -> 'were' [1.0]
                  VVP -> VVBN [1.0]

                  NJJS -> 'most' [1.0]
                  NIN -> 'of' [1.0]
                  NNP2 -> NDT NCD NNNS [1.0]
                  VVBN -> 'shot' [1.0]

                  NCD -> '{year}' [1.0]
                  NNNS -> 'victims' [1.0]
                """

            # The restaurant was also about a half-mile walk away from where most of the [year] victims were shot.
            next_crime_scene_fact = Fact(
                subj=Object(kind=place, attrs={
                    'dist': Object(kind='mile walk', attrs={'obj_mod': 'half',
                                                            'phrase_mod': Phrase(kind='from', attrs={
                                                                'clause_adv': Clause(
                                                                    connective='where',
                                                                    subj=Object(kind='victims',
                                                                                attrs={'event_year': year}),
                                                                    event=Event(kind=self.morphy('shot', 'verb'),
                                                                                passive=True)
                                                                )
                                                            })})
                })
            )

            # The place was deemed secure after the shooting prompted a lockdown for several hours
            last_crime_scene_grammar = f"""
                S -> NP VP [1.0]
                
                NP -> NDT NNN [1.0]
                VP -> VVBD VVP [1.0]
                
                NDT -> 'the' [1.0]
                NNN -> '{place}' [1.0]
                
                VVBD -> 'was' [1.0]
                VVP -> VVBN S2 SBAR [1.0]
                
                VVBN -> 'deemed' [1.0]
                S2 -> ADJP [1.0]
                SBAR -> IN S3 [1.0]
                
                ADJP -> JJ [1.0]
                IN -> 'after' [1.0]
                S3 -> NP2 VP2 [1.0]
                
                JJ -> 'secure' [1.0]
                NP2 -> NDT NNN2 [1.0]
                VP2 -> VVBD2 VNP VPP [1.0]
                
                NNN2 -> '{event}' [1.0]
                VVBD2 -> 'prompted' [1.0]
                VNP -> VDT VNN [1.0]
                VPP -> VIN VNP2 [1.0]
                
                VDT -> '[ARTICLE]' [1.0]
                VNN -> 'lockdown' [1.0]
                VIN -> 'for' [1.0]
                VNP2 -> VJJ VNNS [1.0]
                
                VJJ -> 'several' [1.0]
                VNNS -> 'hours' [1.0]
            """

            # The place was deemed secure after the shooting prompted a lockdown for several hours
            last_crime_scene_fact = Fact(
                subj=Object(kind=place),
                event=Event(kind=self.morphy('deemed', 'verb'),
                            passive=True,
                            attrs={'event_mod': 'secure',
                                   'clause_mod': Clause(connective='after',
                                                        subj=Object(kind=event),
                                                        event=Event(kind=self.morphy('prompted', 'verb')),
                                                        obj=Object(kind='lockdown',
                                                                   attrs={'phrase_mod':
                                                                              Phrase(kind='for',
                                                                                     attrs={'obj': Object(
                                                                                         self.morphy('hours', 'noun'),
                                                                                         attrs={
                                                                                             'obj_mod': 'several'})})}))})
            )

            self.grammar = [crime_scene_grammar, next_crime_scene_grammar, last_crime_scene_grammar]
            self.abstract_fact = [crime_scene_fact, next_crime_scene_fact, last_crime_scene_fact]

        elif self.grammar_type == 2:
            # this should be same as the location in the previous sentence
            # location = 'london'
            # TODO: city should be from the nation
            event = self.metadata['event']

            # when there is  no description
            if 'age' not in self.metadata:
                self.grammar = ''
                self.abstract_fact = None
                return

            age = self.metadata['age']

            crime_scene_grammar = f"""
                S -> NP VP [1.0]
                
                NP -> NNAME COMMA NAGE COMMA [1.0]
                NNAME -> '[NAME]' [1.0]
                COMMA -> ',' [1.0]
                NAGE -> '{age}' [1.0]
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
                
                VVBN -> '{event}' [1.0]
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
            
            NDT -> '[ARTICLE]' [1.0]
            NNN -> 'fight' [1.0]
            VPRT -> VRP [1.0]
            VPP2 -> VIN2 VNP2 [1.0]
            
            VRP -> 'out' [1.0]
            VIN2 -> 'in' [1.0]
            VNP2 -> VNP3 VPP3 [1.0]
            
            VNP3 -> VDT VNN2 [1.0]
            VPP3 -> VIN2 VNP4 [1.0]
            
            VDT -> '[ARTICLE]' [1.0]
            VNN2 -> 'nightclub' [1.0]
            VNP4 -> VNP5 [1.0]
            
            VNP5 -> VDT2 VJJ2 VNN3 [1.0]
            
            VDT2 -> 'the' [1.0]
            VJJ2 -> '[OBJ_MOD]' [1.0]
            VNN3 -> 'resort' [1.0]
            """

            abstract_fact = Fact(
                subj=Person(
                    kind='',  # when the kind is an attribute #NameAttribute(), #'soldier',
                    attrs={
                        # 'name': NameAttribute(),
                        'kind': NameAttribute(),
                        'age': age,
                        # 'location': LocationAttribute()  # TODO: should be a city in his nation
                    }
                ),
                event=Event(
                    kind=self.morphy(event, 'verb'),
                    passive=True,
                    attrs={
                        'subj': NameAttribute(True),
                        'phrase_mod': Phrase(kind='to', attrs={'obj': 'death'}),
                        'clause_adv': Clause(connective='after',
                                             subj=Object(kind='fight'),
                                             event=Event(kind=self.morphy(
                                                 'broke' if self.tense == 'past' else 'breaks', 'verb') + ' out',
                                                         attrs={
                                                             'subj': 'fight',
                                                             'place': Object(kind='nightclub'),
                                                             'place_2': Object(kind='resort',
                                                                               attrs={
                                                                                   'obj_mod': Attribute()
                                                                               }),
                                                             'month': Object(kind='',
                                                                             attrs={'kind': MonthAttribute(),
                                                                                    'obj_mod': 'last'})
                                                         })
                                             )}
                )
            )
            self.grammar = [crime_scene_grammar]
            self.abstract_fact = [abstract_fact]

        add_more = random.choice([0, 1])
        if add_more and event and event in ['shooting', 'shot']:
            crime_scene_grammar_2 = """
                S -> SBAR PRN NP VP [1.0]
                
                SBAR -> SIN S2 [1.0]
                PRN -> COMMA S3 COMMA [1.0]
                NP -> NNN NNNS [1.0]
                VP -> VVBD [1.0]
                
                SIN -> 'as' [1.0]
                S2 -> NP2 VP2 [1.0]
                COMMA -> ',' [1.0]
                S3 -> NP3 VP3 [1.0]
                NNN -> 'city' [1.0]
                NNNS -> 'officials' [1.0]
                VVBD -> 'said' [1.0]
                
                NP2 -> NNN2 NNNS2 [1.0]
                VP2 -> VVBD2 VPP [1.0]
                NP3 -> NPRP [1.0]
                VP3 -> VVBD3 VNP S4 [1.0]
                
                NNN2 -> 'police' [1.0]
                NNNS2 -> 'officers' [1.0]
                VVBD2 -> 'responded' [1.0]
                VPP -> VIN VNP2 [1.0]
                NPRP -> 'they' [1.0]
                VVBD3 -> 'saw' [1.0]
                VNP -> VJJ VJJ2 NNNS3 [1.0]
                S4 -> VP4 [1.0]
                
                VIN -> 'to' [1.0]
                VNP2 -> VDT VNN [1.0]
                VJJ -> 'several' [1.0]
                VJJ2 -> 'young' [1.0]
                NNNS3 -> 'people' [1.0]
                VP4 -> VVBG VPP2 [1.0]
                
                VDT -> 'the' [1.0]
                VNN -> 'scene' [1.0]
                VVBG -> 'running' [1.0]
                VPP2 -> VIN2 VNP3 [1.0]
                VIN2 -> 'from' [1.0]
                VNP3 -> VDT VNN2 [1.0]
                VNN2 -> 'area' [1.0]
            """

            # As police officers responded to the scene, they saw several young people running from the area, city officials said.
            crime_abstract_fact_2 = Fact(
                subj=Person(kind=self.morphy('officials', 'noun'), attrs={'obj_mod': 'city'}),
                event=Event(kind=self.morphy('said', 'verb')),
                obj=Fact(
                    subj=Person(kind='they'),
                    event=Event(kind=self.morphy('saw', 'verb'), attrs={'clause_adv': Clause(connective='as',
                                                                                             subj=Person('officers',
                                                                                                         attrs={
                                                                                                             'obj_mod': 'police'}),
                                                                                             event=Event(
                                                                                                 kind=self.morphy(
                                                                                                     'responded',
                                                                                                     'verb'), attrs={
                                                                                                     'phrase_mod': Phrase(
                                                                                                         kind='to',
                                                                                                         attrs={
                                                                                                             'obj': 'scene'})}))}),
                    obj=Person(kind=self.morphy('people', 'noun'),
                               attrs={'count': 'several', 'age': 'young',
                                      'phrase_mod': Phrase(kind='from', attrs={'obj': 'area'})})
                )
            )

            # for mass shooting
            crime_scene_grammar_3 = """
                S -> NP VP [1.0]
                NP -> NNNS [1.0]
                VP -> VVBD VNP S2 COMMA VPP [1.0]
                
                NNNS -> 'police' [1.0]
                VVBD -> 'called' [1.0]
                VNP -> VDT VNN [1.0]
                S2 -> ADJP [1.0]
                COMMA -> ',' [1.0]
                VPP -> VIN VNP2 [1.0]
                
                VDT -> 'the' [1.0]
                VNN -> 'scene' [1.0]
                ADJP -> AJJ [1.0]
                VIN -> 'with' [1.0]
                VNP2 -> VNP3 VPP2 [1.0]
                
                AJJ -> 'chaotic' [1.0]
                VNP3 -> VQP VNNS [1.0]
                VPP2 -> VIN2 VNP4 [1.0]
                
                VQP -> VJJR VIN3 VCD [1.0]
                VNNS -> 'rounds' [1.0]
                VIN2 -> 'from' [1.0]
                VNP4 -> VNP5 SBAR [1.0]
                SBAR -> WHNP S3 [1.0]
                
                WHNP -> WDT [1.0]
                WDT -> 'that' [1.0]
                S3 -> VP2 [1.0]
                VP2 -> VVBD2 VVP [1.0]
                VVBD2 -> 'were' [1.0]
                
                VJJR -> 'more' [1.0]
                VIN3 -> 'than' [1.0]
                VCD -> '90' [1.0]
                VNP5 -> VJJ VNNS2 [1.0]
                VVP -> VVBN VADVP VPP3 [1.0]
                
                VJJ -> 'multiple' [1.0]
                VNNS2 -> 'guns' [1.0]
                VVBN -> 'fired' [1.0]
                VADVP -> VCC VRB VCC2 VRB2 [1.0]
                VPP3 -> VIN4 VNP6 [1.0]
                
                VCC -> 'both' [1.0]
                VRB -> 'inside' [1.0]
                VCC2 -> 'and' [1.0]
                VRB2 -> 'outside' [1.0]
                VIN4 -> 'of' [1.0]
                VNP6 -> VDT VNN2 [1.0]
                VNN2 -> 'home' [1.0]
            """

            # Pittsburgh Police Chief Scott Schubert called the scene chaotic, with more than 90 rounds from multiple guns fired both inside and outside of the home.
            crime_abstract_fact_3 = Fact(
                subj=Person(kind=self.morphy('police', 'noun')),
                event=Event(kind=self.morphy('called', 'verb')),
                obj=Object(kind=self.morphy('scene', 'noun'),
                           attrs={'obj_mod': 'chaotic', 'phrase_mod': Phrase(kind='with', attrs={
                               'obj': Object(kind=self.morphy('rounds', 'noun'),
                                             attrs={'count': 'more than 90',
                                                    'phrase_mod': Phrase(kind='from',
                                                                         attrs={'obj': Object(
                                                                             kind=self.morphy('guns', 'noun'),
                                                                             attrs={'count': 'multiple',
                                                                                    'clause_rel': Fact(subj=Object(
                                                                                        kind=self.morphy('guns',
                                                                                                         'noun')),
                                                                                        event=Event(
                                                                                            kind=self.morphy(
                                                                                                'fired',
                                                                                                'verb'),
                                                                                            passive=True,
                                                                                            attrs={
                                                                                                'event_mod': Multiple(
                                                                                                    conj='and',
                                                                                                    nodes=[
                                                                                                        Modifier(
                                                                                                            kind='inside',
                                                                                                            attrs={
                                                                                                                'phrase_mod': Phrase(
                                                                                                                    kind='of',
                                                                                                                    attrs={
                                                                                                                        'obj': 'home'})}),
                                                                                                        Modifier(
                                                                                                            kind='outside',
                                                                                                            attrs={
                                                                                                                'phrase_mod': Phrase(
                                                                                                                    kind='of',
                                                                                                                    attrs={
                                                                                                                        'obj': 'home'})})
                                                                                                    ],
                                                                                                    attrs={
                                                                                                        'mod_mod': 'both'})
                                                                                            }))})})})
                           })})
            )

            crime_scene_grammar_4 = """
                S -> S2 NP VP [1.0]
                
                S2 -> NP2 VP2 [1.0]
                COMMA -> ',' [1.0]
                NP -> NDT NNN [1.0]
                VP -> VVBD [1.0]
                
                NP2 -> NPRP [1.0]
                VP2 -> VVBD2 VNP [1.0]
                NDT -> 'the' [1.0]
                NNN -> 'chief' [1.0]
                VVBD -> 'said' [1.0]
                
                NPRP -> '"We' [1.0]
                VVBD2 -> 'saw' [1.0]
                VNP -> VNP2 SBAR [1.0]
                
                VNP2 -> VNNS [1.0]
                SBAR -> WHNP S3 [1.0]
                
                VNNS -> 'people' [1.0]
                WHNP -> WP [1.0]
                S3 -> VP3 [1.0]
                
                WP -> 'who' [1.0]
                VP3 -> VVBD3 VVP [1.0]
                
                VVBD3 -> 'were' [1.0]
                VVP -> VVP2 COMMA VADVP VVP3 [1.0]
                
                VVP2 -> VVBG [1.0]
                VADVP -> VRB [1.0]
                VVP3 -> VVBG2 S4 [1.0]
                
                VVBG -> 'fleeing' [1.0]
                VRB -> 'just' [1.0]
                VVBG2 -> 'trying' [1.0]
                S4 -> VP4 [1.0]
                
                VP4 -> VTO VVP4 [1.0]
                VTO -> 'to' [1.0]
                VVP4 -> VVB VPRT VADVP2 [1.0]
                
                VVB -> 'get' [1.0]
                VPRT -> VRP [1.0]
                VADVP2 -> VRB2 VRB3 [1.0]
                VRP -> 'out' [1.0]
                VRB2 -> 'of' [1.0]
                VRB3 -> 'there."' [1.0]
            """

            # "We saw people who were fleeing, just trying to get out of there," the chief said.
            crime_abstract_fact_4 = Fact(
                subj=Person(kind=self.morphy('chief', 'noun')),
                event=Event(kind=self.morphy('said', 'verb')),
                obj=Fact(
                    subj=Person(kind='we'),
                    event=Event(kind=self.morphy('saw', 'verb')),
                    obj=Person(kind=self.morphy('people', 'noun'),
                               attrs={'clause_rel': Clause(connective='who',
                                                           subj=Person(kind=self.morphy('people', 'noun')),
                                                           event=Event(kind=self.morphy('fleeing', 'verb'))),
                                      'clause_part': Fact(subj=Person(kind=self.morphy('people', 'noun')),
                                                          event=Event(kind=self.morphy('trying', 'verb'), attrs={
                                                              'phrase_mod': Phrase(kind='to',
                                                                                   attrs={'event': Event(
                                                                                       kind=self.morphy('get', 'verb'),
                                                                                       attrs={'phrase_mod': Phrase(
                                                                                           kind='out of',
                                                                                           attrs={
                                                                                               'obj': 'there'})})})
                                                          }))})
                )
            )
            self.grammar += [crime_scene_grammar_2, crime_scene_grammar_4]
            self.abstract_fact += [crime_abstract_fact_2, crime_abstract_fact_4]
