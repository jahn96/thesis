from Attributes.DayAttribute import DayAttribute
from Attributes.LocationAttribute import LocationAttribute
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from generator.Grammar.Grammar import Grammar


class EventDescriptionGrammar(Grammar):
    # Need to pass event to different grammar so that they all talk about the same event!
    def __init__(self, tense: str, grammar_type: int, metadata: dict = None):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = self.metadata['event']
        time = self.metadata['time']
        place = self.metadata['place']
        place_mod = self.metadata['place_mod']

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
                VP2 -> VVBD2 VNP-TMP VPP VPP2 VPP3 [1.0]
                VVBD2 -> 'responded' [1.0]
              """
        else:
            grammar += """
                VP2 -> VVBZ2 VNP-TMP VPP VPP2 VPP3 [1.0]
                VVBZ2 -> 'responds' [1.0]
              """

        grammar += f"""
        VNP-TMP -> VNNP [1.0]
        VPP -> VIN2 VNP [1.0]
        VPP2 -> VIN3 VNP2 [1.0]
        VPP3 -> VIN4 VNP3 [1.0]
        
        VNNP -> '[DAY]' [1.0]
        VIN2 -> 'to' [1.0]
        VNP -> VNP4 VPP4 [1.0]
        
        VNP4 -> VDT VNN [1.0]
        VDT -> 'a' [1.0]
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
        
        VIN4 -> 'at' [1.0]
        VNP3 -> TIME [1.0]
        TIME -> '{time[:-1] if time[-1] == '.' else time}' [1.0]
        """

        # The arrest came after police responded [DAY] to a report of a [EVENT-NOUN] at [LOCATION] at [TIME] p.m.
        abstract_fact = Fact(
            subj=Object(kind='arrest'),
            event=Event(kind=self.stemmer.stem('came'),
                        attrs={'subj': 'arrest',
                               'clause_mod': Object(kind='after', attrs={
                                                                         'clause': Fact(
                                   subj=Object(kind='police'),
                                   event=Event(
                                       kind=self.stemmer.stem('responded' if self.tense == 'past' else 'responds'),
                                       attrs={
                                           'day': DayAttribute(),
                                           'subj': 'police',
                                           'phrase_mod': Object(kind='to', attrs={'obj': Object(kind='report', attrs={
                                                                                  'phrase_mod': Object(kind='of',
                                                                                                       attrs={
                                                                                                           'obj': Object(
                                                                                                               kind=event,
                                                                                                               attrs={
                                                                                                                   'place': Object(kind=place, attrs={'obj_mod': place_mod}),
                                                                                                                   'time': time
                                                                                                               }),
                                                                                                       })})})

                                       })
                               )})}
                        ))

        self.grammar = grammar
        self.abstract_fact = abstract_fact

        next_grammar = """
        S -> NP VP [1.0]
        NP -> NDT NNN [1.0]
        NDT -> 'The' [1.0]
        NNN -> 'place' [1.0]
        """

        if self.tense == 'past':
            next_grammar += """
                VP -> VVBD VVP [1.0]
                VVBD -> 'was' [1.0]
            """
        else:
            next_grammar += """
                VP -> VVBZ VVP [1.0]
                VVBZ -> 'is' [1.0]
            """

        next_grammar += """
        VVP -> VVBN S2 [0.5] | VVBN S2 VSBAR [0.5]
        VVBN -> 'deemed' [1.0]
        S2 -> ADJP [1.0]
        VSBAR -> VIN S3 [1.0]
        
        ADJP -> AJJ APP [1.0]
        VIN -> 'after' [1.0]
        S3 -> NP2 VP2 [1.0]
        
        AJJ -> 'secure' [1.0]
        APP -> AIN ANP [1.0]
        NP2 -> NDT2 NNN2 [1.0]
        """

        if self.tense == 'past':
            next_grammar += """
            VP2 -> VVBD2 VNP VPP [1.0]
            VVBD2 -> 'prompted' [1.0]
        """
        else:
            next_grammar += """
            VP2 -> VVBZ2 VNP VPP [1.0]
            VVBZ2 -> 'prompts' [1.0]
        """

        next_grammar += """
        AIN -> 'at' [1.0]
        ANP -> ACD ARB ANNP [1.0]
        ACD -> '[TIME]' [1.0]
        ARB -> 'a.m.' [1.0]
        ANNP -> '[NEXT_DAY]' [1.0]
        NDT2 -> 'the' [1.0]
        NNN2 -> '[EVENT-NOUN]' [1.0]
        VNP -> VDT VNN [1.0]
        VPP -> VIN2 VNP2 [1.0]
        
        VDT -> 'a' [1.0]
        VNN -> 'lockdown' [1.0]
        VIN2 -> 'for' [1.0]
        VNP2 -> VJJ VNNS [1.0]
        VJJ -> 'several' [1.0]
        VNNS -> 'hours' [1.0]
        """

        # part 2:  The stabbing took place during a fight between 1 french soldier and 2 french tourists at this nightclub.
