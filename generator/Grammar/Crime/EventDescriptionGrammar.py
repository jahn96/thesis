from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar
from generator.Grammar.grammar_utils import get_next_day


class EventDescriptionGrammar(Grammar):
    """
    Grammar that describes the crime event
    """

    # Need to pass event to different grammar so that they all talk about the same event!
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):

        if self.grammar_type == 1:
            event = self.metadata['event']
            place = self.metadata['place']
            place_mod = self.metadata['place_mod']
            day = self.metadata['day']

            next_day = get_next_day(day)

            grammar = """
              S -> NP VP [1.0]
              NP -> NDT NNN [1.0]
              NDT -> 'the' [1.0]
              NNN -> 'arrest' [1.0]
            """

            if self.tense == 'past':
                grammar += """
                    VP -> VVBD VSBAR [1.0]
                    VVBD -> 'came' [1.0]
                  """
            else:
                grammar += """
                    VP -> VVBZ VSBAR [1.0]
                    VVBZ -> 'comes' [1.0]
                  """
            grammar += """
            VSBAR -> VIN S2 [1.0]
            VIN -> 'after' [1.0]
            S2 -> NP2 VP2 [1.0]
            
            NP2 -> NNNS [1.0]
            NNNS -> 'police' [1.0]
            """

            if self.tense == 'past':
                grammar += """
                    VP2 -> VVBD2 VNP-TMP VPP VPP2 [1.0]
                    VVBD2 -> 'responded' [1.0]
                  """
            else:
                grammar += """
                    VP2 -> VVBZ2 VNP-TMP VPP VPP2 [1.0]
                    VVBZ2 -> 'responds' [1.0]
                  """

            grammar += f"""
            VNP-TMP -> VNNP [1.0]
            VPP -> VIN2 VNP [1.0]
            VPP2 -> VIN3 VNP2 [1.0]
            
            VNNP -> '{next_day}' [1.0]
            VIN2 -> 'to' [1.0]
            VNP -> VNP4 VPP4 [1.0]
            
            VNP4 -> VDT VNN [1.0]
            VDT -> '[ARTICLE]' [1.0]
            VNN -> 'report' [1.0]
            
            VPP4 -> VIN5 VNP5 [1.0]
            VIN5 -> 'of' [1.0]
            VNP5 -> VDT2 VNN2 [1.0]
            VDT2 -> 'the' [1.0]
            VNN2 -> '{event}' [1.0]
            
            VIN3 -> 'at' [1.0]
            VNP2 -> VDT2 VJJ VNN3 [1.0]
            VJJ -> '{place_mod}' [1.0]
            VNN3 -> '{place}' [1.0]
            """

            # The arrest came after police responded [DAY] to a report of a [EVENT-NOUN] at [LOCATION] at [TIME] p.m.
            abstract_fact = Fact(
                subj=Object(kind='arrest'),
                event=Event(kind=self.morphy('came', 'verb'),
                            attrs={
                                'clause_sub': Clause(connective='after',
                                                     subj=Object(kind='police'),
                                                     event=Event(
                                                         kind=self.morphy(
                                                             'responded' if self.tense == 'past' else 'responds', 'verb'),
                                                         attrs={
                                                             'day': next_day,
                                                             'phrase_mod': Phrase(kind='to',
                                                                                  attrs={'obj': Object(kind='report',
                                                                                                       attrs={
                                                                                                           'phrase_mod': Phrase(
                                                                                                               kind='of',
                                                                                                               attrs={
                                                                                                                   'obj': Object(
                                                                                                                       kind=event,
                                                                                                                       attrs={
                                                                                                                           'place': Object(
                                                                                                                               kind=place,
                                                                                                                               attrs={
                                                                                                                                   'obj_mod': place_mod}),
                                                                                                                       }),
                                                                                                               })})})

                                                         })
                                                     )})
            )

            self.grammar = grammar
            self.abstract_fact = abstract_fact

            # next_grammar = """
            # S -> NP VP [1.0]
            # NP -> NDT NNN [1.0]
            # NDT -> 'The' [1.0]
            # NNN -> 'place' [1.0]
            # """
            #
            # if self.tense == 'past':
            #     next_grammar += """
            #         VP -> VVBD VVP [1.0]
            #         VVBD -> 'was' [1.0]
            #     """
            # else:
            #     next_grammar += """
            #         VP -> VVBZ VVP [1.0]
            #         VVBZ -> 'is' [1.0]
            #     """
            #
            # next_grammar += """
            # VVP -> VVBN S2 [0.5] | VVBN S2 VSBAR [0.5]
            # VVBN -> 'deemed' [1.0]
            # S2 -> ADJP [1.0]
            # VSBAR -> VIN S3 [1.0]
            #
            # ADJP -> AJJ APP [1.0]
            # VIN -> 'after' [1.0]
            # S3 -> NP2 VP2 [1.0]
            #
            # AJJ -> 'secure' [1.0]
            # APP -> AIN ANP [1.0]
            # NP2 -> NDT2 NNN2 [1.0]
            # """
            #
            # if self.tense == 'past':
            #     next_grammar += """
            #     VP2 -> VVBD2 VNP VPP [1.0]
            #     VVBD2 -> 'prompted' [1.0]
            # """
            # else:
            #     next_grammar += """
            #     VP2 -> VVBZ2 VNP VPP [1.0]
            #     VVBZ2 -> 'prompts' [1.0]
            # """
            #
            # next_grammar += """
            #     AIN -> 'at' [1.0]
            #     ANP -> ACD ARB ANNP [1.0]
            #     ACD -> '[TIME]' [1.0]
            #     ARB -> 'a.m.' [1.0]
            #     ANNP -> '[NEXT_DAY]' [1.0]
            #     NDT2 -> 'the' [1.0]
            #     NNN2 -> '[EVENT-NOUN]' [1.0]
            #     VNP -> VDT VNN [1.0]
            #     VPP -> VIN2 VNP2 [1.0]
            #
            #     VDT -> 'a' [1.0]
            #     VNN -> 'lockdown' [1.0]
            #     VIN2 -> 'for' [1.0]
            #     VNP2 -> VJJ VNNS [1.0]
            #     VJJ -> 'several' [1.0]
            #     VNNS -> 'hours' [1.0]
            # """
            #
            # # The place was deemed secure at [TIME] a.m. [NEXT_DAY].
            # next_abstract_fact = Fact(
            #     subj=Object(kind='place'),
            #     event=Event(kind=self.stemmer.stem('deemed'), passive=True, attrs={
            #         'event_mod': 'secure',
            #         'time': TimeAttribute(),
            #
            #     })
            # )
            # self.grammar = next_grammar

        # part 2:  The stabbing took place during a fight between 1 french soldier and 2 french tourists at this nightclub.
        elif self.grammar_type == 2:
            num_soldiers = self.metadata['num_soldiers']
            num_tourists = self.metadata['num_tourists']
            soldier_nationality = self.metadata['soldier_nationality']
            tourist_nationality = self.metadata['tourist_nationality']
            event = self.metadata['event']

            crime_sub_headline_grammar = f"""
                  S -> NP VP [1.0]

                  NP -> NDT NNN [1.0]
                  NDT -> 'The' [1.0]
                  NNN -> '{event}' [1.0]
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

              VDT2 -> '[ARTICLE]' [1.0]
              VNN3 -> 'fight' [1.0]
              VIN3 -> 'between' [1.0]
              VNP5 -> VNP6 VCC VNP7 [1.0]
              """

            if self.num_text_int_map[num_soldiers] < 2:
                crime_sub_headline_grammar += """
                  VNP6 -> VCD1 VNATIONALITY VNN4 [1.0]
                  VNN4 -> 'soldier' [1.0]
              """
            else:
                crime_sub_headline_grammar += """
                VNP6 -> VCD1 VNATIONALITY VNNS [1.0]
                VNNS -> 'soldiers' [1.0]
              """

            if self.num_text_int_map[num_tourists] < 2:
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
                subj=Object(kind=event),
                event=Event(kind=self.morphy('took', 'verb'),
                            attrs={
                                'subj': event,
                                'obj': 'place',
                                'phrase_mod':
                                    Phrase(kind='during', attrs={'obj':
                                                                     Object(kind='fight',
                                                                            attrs={
                                                                                'place': 'nightclub',
                                                                                'phrase_mod':
                                                                                    Phrase(kind='between',
                                                                                           attrs={'obj':
                                                                                                      Multiple(
                                                                                                          conj='and',
                                                                                                          nodes=[Person(
                                                                                                              kind='soldier',
                                                                                                              attrs={
                                                                                                                  'nationality': soldier_nationality,
                                                                                                                  'count': str(num_soldiers)}),
                                                                                                              Person(
                                                                                                                  kind='tourist',
                                                                                                                  attrs={
                                                                                                                      'nationality': tourist_nationality,
                                                                                                                      'count': str(num_tourists)
                                                                                                                  })])})})})})
            )
            self.grammar = crime_sub_headline_grammar
            self.abstract_fact = abstract_fact
