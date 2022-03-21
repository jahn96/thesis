"""
"Our lives were completely destroyed," she said, wiping tears. The victim's brother closed his business and left Nashville.
"This has broken me, not just my spirit, not just my family, but also my mind," she said, her voice trembling. "This has broken me mentally."

"My son Akilah was a beautiful soul who perfected how to be a son," she cried. "My sweet baby, my angel, my son was robbed of his life."

# when the victim is university student. -> Sands wrote that the university's "condolences go out to the family and friends of the deceased and we extend our support to those who were injured."

"It's weird to hear about it happening so close to your house. I work right down the street, like, I live here. So it's hard," Lopus told WSLS.
"""
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from generator.Grammar.Grammar import Grammar


class CrimeQuoteGrammar(Grammar):
    """
    NOTE: crime quote grammar doesn't parse facts inside the quote !
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        grammar = """
          S -> QUOTE S2 COMMA CC S3 [1.0]
    
          S2 -> S4 COMMA RB S5 [1.0]
          COMMA -> ',' [1.0]
          CC -> 'but' [1.0]
          S3 -> ADVP NP VP [1.0]
    
          S4 -> NP2 VP2 [1.0]
          RB -> 'not' [1.0]
          S5 -> ADVP2 NP3 [1.0]
          ADVP -> ARB [1.0]
          NP -> NNP COMMA NNP2 [1.0]
          VP -> VVBD COMMA S6 [1.0]
    
          NP2 -> NDT [1.0]
          VP2 -> VVBZ VVP [1.0]
          ADVP2 -> ARB2 [1.0]
          NP3 -> NNP3 COMMA NCONJP NNP4 [1.0]
          ARB -> 'also' [1.0]
          NNP -> NPRP NNN QUOTE [1.0]
          NNP2 -> NNP5 NNN2 [1.0]
          VVBD -> 'said' [1.0]
          S6 -> NP4 VP3 [1.0]
    
          NDT -> 'This' [1.0]
          VVBZ -> 'has' [1.0]
          VVP -> VBN VNP [1.0]
          ARB2 -> 'just' [1.0]
          NNP3 -> NPRP2 NNN3 [1.0]
          NCONJP -> NRB NRB2 [1.0]
          NNP4 -> NPRP3 NNN4 [1.0]
          NPRP -> 'my' [1.0]
          NNN -> 'mind' [1.0]
          NNP5 -> NDT2 NNN5 NPOS [1.0]
          NNN2 -> 'mom' [1.0]
          NP4 -> NPRP4 NNN6 [1.0]
          VP3 -> VVBG [1.0]
    
          VBN -> 'broken' [1.0]
          VNP -> VPRP [1.0]
          NPRP2 -> 'my' [1.0]
          NNN3 -> 'spirit' [1.0]
          NRB -> 'not' [1.0]
          NRB2 -> 'just' [1.0]
          NPRP3 -> 'my' [1.0]
          NNN4 -> 'family' [1.0]
          NDT2 -> 'the' [1.0]
          NNN5 -> 'victim' [1.0]
          NPOS -> "'s" [1.0]
          NPRP4 -> 'her' [1.0]
          NNN6 -> 'voice' [1.0]
          VVBG -> 'trembling' [1.0]
    
          VPRP -> 'me' [1.0]
          QUOTE -> '"' [1.0]
        """

        # TODO: ask Foaad about handling this quote ! because summarizer could use the part of quote in the summary
        # "This has broken me, not just my spirit, not just my family, but also my mind", the victim's mom said, her voice trembling.
        abstract_fact = Fact(
            subj=Person(kind='mom', attrs={"poss": Person(kind='victim')}),
            event=Event(kind=self.stemmer.stem('said'),
                        # clause comp = clause complement
                        attrs={'subj': 'mom', 'clause_comp': Event(kind=self.stemmer.stem(
                            'trembling'),
                            attrs={'subj': Object(kind='voice', attrs={'poss': 'her'})})})
        )

        self.grammar = grammar
        self.abstract_fact = abstract_fact

        return grammar
