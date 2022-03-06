import random

from Attributes.AgeAttribute import AgeAttribute
from Attributes.Attribute import Attribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from generator.Grammar.Grammar import Grammar


class OutfitDescriptionGrammar(Grammar):
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None, obj: str = "man"):
        super().__init__(tense, grammar_type, metadata)
        self.__obj = obj
        self.num_ordinal_map = {
            1: 'first',
            2: 'second',
            3: 'third'
        }

    def define_grammar(self):
        """
        Generate PCFG grammars

        Parameters:
        tense (string): tense of grammar such as past or present
        """

        # There was no description for one of the men
        crime_desc_grammar_1 = """
            S -> NP VP [1.0]
        
            NP -> NEX [1.0]
            NEX -> 'There' [1.0]
        """

        if self.tense == 'present':
            crime_desc_grammar_1 += """
                VP -> VVBZ VNP [1.0]
                VVBZ -> 'is' [1.0]
            """
        else:
            crime_desc_grammar_1 += """
                VP -> VVBD VNP [1.0]
                VVBD -> 'was' [1.0]
            """

        crime_desc_grammar_1 += f"""
            VNP -> VNP2 VPP [1.0]
            
            VNP2 -> VDT VNN [1.0]
            VPP -> VIN VNP3 [1.0]
            
            VDT -> 'no' [1.0]
            VNN -> 'description' [1.0]
            VIN -> 'for' [1.0]
            """

        if 'ordinal' in self.metadata:
            ordinal = self.num_ordinal_map[self.metadata['ordinal']]
            crime_desc_grammar_1 += f"""
                VNP3 -> VDT2 VJJ VNN2 [1.0]
                VDT2 -> 'the'                  [1.0]
                VJJ -> '{ordinal}'    [1.0]
                VNN2 -> '{self.__obj}'         [1.0]
            """
        else:
            crime_desc_grammar_1 += f"""
                VNP3 -> VDT2 VNN2 [1.0]
                VDT2 -> 'the'                  [1.0]
                VNN2 -> '{self.__obj}'         [1.0]
            """

        if 'ordinal' in self.metadata:
            ordinal = self.num_ordinal_map[self.metadata['ordinal']]

            crime_desc_grammar_2 = f"""
                S -> NP VP [1.0]
                NP -> NDT NJJ NNN                  [1.0]
                NDT -> 'the'                   [1.0]
                NJJ -> '{ordinal}' [1.0]
                NNN -> '{self.__obj}'                  [1.0]
            """
        else:
            crime_desc_grammar_2 = f"""
                S -> NP VP [1.0]
                NP -> NDT NNN                  [1.0]
                NDT -> 'the'                   [1.0]
                NNN -> '{self.__obj}'          [1.0]
            """

        if self.tense == 'present':
            crime_desc_grammar_2 += """
                VP -> VVBZ VNP [1.0]
                VVBZ -> 'has' [1.0]
            """
        else:
            crime_desc_grammar_2 += """
                VP -> VVBD VNP [1.0]
                VVBD -> 'had' [1.0]
            """

        crime_desc_grammar_2 += """
            VNP -> VDT VNN [1.0]      
            VDT -> 'no' [1.0]
            VNN -> 'description' [1.0]
        """

        if 'ordinal' in self.metadata:
            ordinal = self.num_ordinal_map[self.metadata['ordinal']]

            crime_desc_grammar_3 = f"""
                S -> NP VP                     [1.0]
                NP -> NDT NJJ NNN                  [1.0]
                NDT -> 'the'                   [1.0]
                NJJ -> '{ordinal}' [1.0]
                NNN -> '{self.__obj}'                  [1.0]
            """
        else:
            crime_desc_grammar_3 = f"""
                S -> NP VP                     [1.0]
                NP -> NDT NNN                  [1.0]
                NDT -> 'the'                   [1.0]
                NNN -> '{self.__obj}'          [1.0]
            """
        if self.tense == 'present':
            crime_desc_grammar_3 += """
                VP -> VVBZ VVP [1.0]
                VVBZ -> 'is' [1.0]
            """
        else:
            crime_desc_grammar_3 += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'was' [1.0]
            """

        crime_desc_grammar_3 += f"""
            VVP -> VVBN VPP                [1.0]
            VVBN -> 'described'            [1.0]
            VPP -> VIN VNP [0.5] | VIN VS [0.5]
            
            VS -> VVP2                     [1.0]
            
            VVP2 -> VVBG VSNP              [1.0]
            
            VVBG -> 'wearing'              [1.0]
            VSNP -> VSNP2 VCC VSNP3        [1.0]
            
            VSNP2 -> VDT VJJ2 VNN2         [1.0]
            VSNP3 -> VJJ4 VNNS3            [1.0]
            
            VIN -> 'as'                    [1.0]
            VNP -> VNP2 COMM VP2           [1.0]
            VNP2 -> VADJP                  [1.0]
            COMM -> ','                    [1.0]
            VP2 -> VBG VNP3 COMM VPP2      [1.0]
            
            VADJP -> VNP4          [1.0]
            VBG -> 'wearing'               [1.0]
            VNP3 -> VNP5 VPP3              [1.0]
            VPP2 -> VIN2 VNP6              [1.0]
            
            VNP4 -> VQP            [1.0]
            VNP5 -> VDT VJJ2 VNN2          [1.0]
            VPP3 -> VIN3 VNP7              [1.0]
            VIN2 -> 'with'                 [1.0]
            VNP6 -> VUCP VNNS              [1.0]
            
            VQP -> VRB VAGE                 [1.0]
            VJJ2 -> '[OBJ_MOD]'        [1.0]
            VNN2 -> 'jacket'               [1.0]
            VIN3 -> 'with'                 [1.0]
            VNP7 -> VNP8 VCC VNP9          [1.0]
            VUCP -> VNML VCC VADJP2        [1.0]
            VNNS -> 'shoes'                [1.0]
            
            VRB -> 'about'                 [1.0]
            VAGE -> '[AGE]'                [1.0]
            VNP8 -> VDT VJJ3 VNN3          [1.0]
            VCC -> 'and'                   [1.0]
            VNP9 -> VNNS2             [1.0]
            VNML -> VJJ5 VNNS3             [1.0]
            VADJP2 -> VJJ6                 [1.0]
            
            VDT -> 'a'                     [1.0]
            VJJ3 -> '[OBJ_MOD]'              [1.0]
            VNN3 -> 'collar'               [1.0]
            VNNS2 -> 'cuffs'               [1.0]
            VJJ5 -> '[OBJ_MOD]'          [1.0]
            VNNS3 -> 'jeans'               [1.0]
            VJJ6 -> '[OBJ_MOD]'          [1.0]
        """

        desc_grammars = [crime_desc_grammar_1, crime_desc_grammar_2, crime_desc_grammar_3]
        chosen_idx = random.choices(range(len(desc_grammars)), weights=[0.1, 0.1, 0.8])[0]
        self.grammar = desc_grammars[chosen_idx]

        if chosen_idx == 0:
            fact = Fact(obj=Object(kind='description',
                                   neg=True,
                                   attrs={'phrase_mod': Object(kind='for', attrs={'obj': Person(kind=self.__obj,
                                                                                                attrs={
                                                                                                    'ordinal':
                                                                                                        self.num_ordinal_map[
                                                                                                            self.metadata[
                                                                                                                'ordinal']]
                                                                                                        if 'ordinal' in self.metadata
                                                                                                        else None})})}))
            self.abstract_fact = fact

        # TODO: change event kind according to the tense
        elif chosen_idx == 1:
            verb = 'have' if self.tense == 'present' else 'had'
            fact = Fact(subj=Person(kind=self.__obj, attrs={
                'ordinal': self.num_ordinal_map[self.metadata['ordinal']] if 'ordinal' in self.metadata else None}),
                        event=Event(kind=self.stemmer.stem(verb), attrs={'subj': self.__obj, 'obj': 'description'}),
                        obj=Object(kind='description', neg=True))
            self.abstract_fact = fact

        else:
            # TODO: check if we need to have object kind as a part of phrase mod attribute in fact table
            # described as about 70-year old , wearing a zipped jacket with a red collar and cuffs , with skinny jeans and casual shoes.
            verb = 'is described' if self.tense == 'present' else 'was described'
            fact = Fact(subj=Person(kind=self.__obj,
                                    attrs={'ordinal': self.num_ordinal_map[
                                        self.metadata['ordinal']] if 'ordinal' in self.metadata else None,
                                           'age': AgeAttribute(),
                                           'clause_mod': Fact(
                                               event=Event(kind=self.stemmer.stem('wearing'),
                                                           attrs={'subj': self.__obj,
                                                                  'obj': 'jacket',
                                                                  'phrase_mod': Object(kind='with', attrs={'obj': [
                                                                      Object(kind='jeans',
                                                                             attrs={'obj_mod': Attribute()}),
                                                                      Object(kind='shoes',
                                                                             attrs={
                                                                                 'obj_mod': Attribute()})
                                                                  ]})}),
                                               obj=[Object(kind='jacket', attrs={
                                                   'obj_mod': Attribute(),
                                                   'phrase_mod': Object(kind='with', attrs={'obj':
                                                                                                [Object(kind='collar',
                                                                                                        attrs={
                                                                                                            'obj_mod': Attribute()}),
                                                                                                 Object(kind='cuffs')
                                                                                                 ]})}),
                                                    ])
                                           }),
                        event=Event(kind=self.stemmer.stem(verb), attrs={'subj': self.__obj}))
            self.abstract_fact = fact
