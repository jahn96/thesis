# TODO: format it in a Grammar.py
# simple grammar
def define_grammar(tense, attrs):
    """
    This function defines context-free grammar

    Parameters:
    tense (string): tense of a grammar
    attrs (list of string): a list of attributes

    Returns:
    string: context-free grammar

    """
    grammar = ""

    if len(attrs) == 1:
        if attrs[0] == 'color':
            grammar = """
        S -> NP VP
        NP -> DT NNS
        DT -> 'A'
        NNS -> '[obj]'
      """

            if tense == 'present':
                grammar += """
          VP -> VBZ NPO
          VP -> VBBZ VPZ
          VP -> VBBZ JJ
          VBZ -> 'has'
          VBBZ -> 'is'
        """
            else:
                grammar += """
          VP -> VBD NPO
          VP -> VBBD VPZ
          VP -> VBBD JJ
          VBD -> 'had'
          VBBD -> 'was'
        """
            grammar += """
        NPO -> JJ NNO
        JJ -> '[color]'
        NNO -> 'color'
    
        VPZ -> VBN PPZ
        VBN -> 'colored'
        PPZ -> INZ NNZ
        PPZ -> INZ NNZO
        INZ -> 'in'
        NNZO -> '[color]'
        NNZ -> NNZO O
        O -> 'color'
      """

        elif attrs[0] == 'location':
            grammar = """
        S -> NP VP
        NP -> DT NN
        DT -> 'A'
        NN -> '[obj]'
      """
            if tense == 'present':
                grammar += """
          VP -> VBZ VPZ
          VP -> VBZ PPZ
          VBZ -> 'is'
        """
            else:
                grammar += """
          VP -> VBD VPZ
          VP -> VBD PPZ
          VBD -> 'was'
        """
            grammar += """
        VPZ -> VBN PPZ
        VBN -> 'located' | 'placed'
        PPZ -> INO NNO
        INO -> 'in'
        NNO -> '[location]'
      """

    elif len(attrs) == 2:
        grammar = """
      S -> NP VP
      NP -> NPS PPS
      NPS -> NNS
      NNS -> '[obj]'
      PPS -> IN NPP
      IN -> 'with'
      NPP -> JJ NNP
      JJ -> '[color]'
      NNP -> 'color' """

        if tense == 'present':
            grammar += """
        VP -> VBZ VPZ
        VP -> VBZ PPZ
        VBZ -> 'is'
      """
        else:
            grammar += """
        VP -> VBD VPZ
        VP -> VBD PPZ
        VBD -> 'was'
      """
        grammar += """
      VPZ -> VBN PPZ
      VBN -> 'located' | 'placed'
      PPZ -> INO NNO
      INO -> 'in'
      NNO -> '[location]'
    """
    return grammar
