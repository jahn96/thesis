from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from generator.Grammar.Grammar import Grammar


class EventSubHeadLineGrammar(Grammar):
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        if self.grammar_type == 2:
            num_soldiers = self.metadata['num_soldiers']
            num_tourists = self.metadata['num_tourists']
            soldier_nationality = self.metadata['soldier_nationality']
            tourist_nationality = self.metadata['tourist_nationality']

            crime_sub_headline_grammar = f"""
                  S -> NP VP [1.0]

                  NP -> NDT NNN [1.0]
                  NDT -> 'The' [1.0]
                  NNN -> 'stabbing' [1.0]
                  """
            if self.tense == 'present':
                crime_sub_headline_grammar += """
                VP -> VVBZ VNP VPP VPP2 [1.0]
                VVBZ -> 'takes' [1.0]
              """
            else:
                crime_sub_headline_grammar += """
                VP -> VVBD VNP VPP VPP2 [1.0]
                VVBD -> 'took' [1.0]
              """

            crime_sub_headline_grammar += """
              VNP -> VNN [1.0]
              VPP -> VIN VNP2 [1.0]
              VPP2 -> VIN2 VNP3 [1.0]
    
              VNN -> 'place' [1.0]
              VIN -> 'during' [1.0]
              VNP2 -> VNP4 VPP3 [1.0]
              VIN2 -> 'at' [1.0]
              VNP3 -> VDT VNN2 [1.0]
    
              VNP4 -> VDT2 VNN3 [1.0]
              VPP3 -> VIN3 VNP5 [1.0]
              VDT -> 'this' [1.0]
              VNN2 -> 'nightclub' [1.0]
    
              VDT2 -> 'a' [1.0]
              VNN3 -> 'fight' [1.0]
              VIN3 -> 'between' [1.0]
              VNP5 -> VNP6 VCC VNP7 [1.0]
              """

            if num_soldiers < 2:
                crime_sub_headline_grammar += """
                  VNP6 -> VCD1 VNATIONALITY VNN4 [1.0]
                  VNN4 -> 'soldier' [1.0]
              """
            else:
                crime_sub_headline_grammar += """
                VNP6 -> VCD1 VNATIONALITY VNNS [1.0]
                VNNS -> 'soldiers' [1.0]
              """

            if num_tourists < 2:
                crime_sub_headline_grammar += """
                VNP7 -> VCD2 VNATIONALITY2 VNN5 [1.0]
                VNN5 -> 'tourist' [1.0]
              """
            else:
                crime_sub_headline_grammar += """
                VNP7 -> VCD2 VNATIONALITY2 VNNS2 [1.0]
                VNNS2 -> 'tourists' [1.0]
              """
            crime_sub_headline_grammar += f"""
              VCC -> 'and' [1.0]
    
              VCD1 -> '{num_soldiers}' [1.0]
              VNATIONALITY -> '{soldier_nationality}' [1.0]
              VNATIONALITY2 -> '{tourist_nationality}' [1.0]
              VCD2 -> '{num_tourists}' [1.0]
            """
            #  The stabbing took place during a fight between 1 french soldier and 2 french tourists at this nightclub.
            abstract_fact = Fact(
                subj=Object(kind='stabbing'),
                event=Event(kind=self.stemmer.stem('took'),
                            attrs={
                                'subj': 'stabbing',
                                'obj': 'place',
                                'phrase_mod':
                                    Object(kind='during', attrs={'obj':
                                                                     Object(kind='fight',
                                                                            attrs={
                                                                                'place': 'nightclub',
                                                                                'phrase_mod':
                                                                                    Object(kind='between',
                                                                                           attrs={'obj':
                                                                                               [Object(
                                                                                                   kind='soldier',
                                                                                                   attrs={
                                                                                                       'nationality': soldier_nationality,
                                                                                                       'count': num_soldiers}),
                                                                                                   Object(
                                                                                                       kind='tourist',
                                                                                                       attrs={
                                                                                                           'nationality': tourist_nationality,
                                                                                                           'count': num_tourists
                                                                                                       })]})})})})
            )
            self.grammar = crime_sub_headline_grammar
            self.abstract_fact = abstract_fact
