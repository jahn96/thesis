from nltk.parse.generate import generate

tense = 'past'

# TODO: think about the probablistic grammar (where with 0.5 percentage, it gives longer sentence - how will you reflect this on the fact?

crime_grammar_2 = """
  S -> NP COMMA S2 COMMA VP [1.0]

  NP -> NNAME [1.0]
  COMMA -> ',' [1.0]
  S2 -> UCP [1.0]
  """

if tense == 'present':
    crime_grammar_2 += """
VP -> VVBZ2 VVP [1.0]
VVBZ2 -> 'is' [1.0]
"""

else:
    crime_grammar_2 += """
VP -> VVBD2 VVP [1.0]
VVBD2 -> 'was' [1.0]
"""

crime_grammar_2 += """
NNAME -> '[NAME]' [1.0]
UCP -> UPP COMMA UCC S3 [1.0]
VVP -> VVBN VCC VVBN2 VNP [1.0]

UPP -> UADVP UIN UNATIONALITY [1.0]
UCC -> 'but' [1.0]
S3 -> VP2 [1.0]
VVBN -> 'provoked' [1.0]
VCC -> 'and' [1.0]
VVBN2 -> 'lost' [1.0]
VNP -> VNP2 VSBAR2 [0.1] | VNP2 [0.9]

UADVP -> URB [1.0]
UIN -> 'from' [1.0]
UNATIONALITY -> '[NATIONALITY]' [1.0]
VP2 -> VBG VPP [1.0]
VNP2 -> VNN HYPH VNN2 [1.0]
VSBAR2 -> VWHADVP S4 [1.0]

URB -> 'originally' [1.0]
VBG -> 'living' [1.0]
VPP -> VIN2 VCITY [1.0]
VNN -> 'self' [1.0]
HYPH -> '-' [1.0]
VNN2 -> 'control' [1.0]
VWHADVP -> VWRB [1.0]
S4 -> NP2 VP3 [1.0]

VIN2 -> 'in' [1.0]
VCITY -> '[CITY]' [1.0]
VWRB -> 'when' [1.0]
NP2 -> NPRP [1.0]
VP3 -> VVP2 VCC VADVP VVP3 [1.0]
"""

if tense == 'present':
    crime_grammar_2 += """
    VVP2 -> VVBZ3 VPRT VNP3 [1.0]
    VVP3 -> VVBZ4 VNAME [1.0]
    VVBZ3 -> 'pulled' [1.0]
    VVBZ4 -> 'stabbed' [1.0]
    """
else:
    crime_grammar_2 += """
    VVP2 -> VVBD3 VPRT VNP3 [1.0]
    VVP3 -> VVBD4 VNAME [1.0]
    VVBD3 -> 'pulled' [1.0]
    VVBD4 -> 'stabbed' [1.0]
    """
crime_grammar_2 += """
    NPRP -> 'he' [1.0]
    VADVP -> VRB [1.0]
    
    VPRT -> VRP [1.0]
    VNP3 -> VDT VNN3 [1.0]
    VRB -> 'fatally' [1.0]
    VNAME -> '[NAME]' [1.0]
    
    VRP -> 'out' [1.0]
    VDT -> 'a' [1.0]
    VNN3 -> 'switchblade' [1.0]
"""

if __name__ == '__main__':
    import nltk

    pcfg_grammar = nltk.PCFG.fromstring(crime_grammar_2)

    for sent in generate(pcfg_grammar, n=1):
        datum = (' '.join(sent)).capitalize() + '.'
        print(datum)
