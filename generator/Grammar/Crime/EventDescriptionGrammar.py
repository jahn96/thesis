from generator.Grammar.Grammar import Grammar

# TODO: add this!
class EventDescriptionGrammar(Grammar):
    # Need to pass event to different grammar so that they all talk about the same event!
    def __init__(self, tense: str, metadata: dict = None):
        super().__init__(tense, metadata)

    def define_grammar(self):
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
        
        NP2 -> NNNP NNNS [1.0]
        NNNP -> '[CITY]' [1.0]
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

        grammar += """
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
        VNP5 -> VDT VNN2 [1.0]
        VNN2 -> '[EVENT-NOUN]' [1.0]
        
        VIN3 -> 'at' [1.0]
        VNP2 -> '[LOCATION]' [1.0]
        
        VIN4 -> 'at' [1.0]
        VNP3 -> VCD VRB [1.0]
        VCD -> '[TIME]' [1.0]
        VRB -> 'p.m' [1.0]
        """
        # TIME needs to be late night

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