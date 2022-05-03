from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Person import Person
from generator.Grammar.Grammar import Grammar

class SurvivorQuoteGrammar(Grammar):
    """
    Grammar that outputs the quote from a survivor
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)
        self.last_quote = None

    def define_grammar(self):
        survivor_quote_grammar = """
            S -> NP VP [1.0]
            NP -> NPRP [1.0]
            VP -> VVBD VADJP [1.0]
            
            NPRP -> '"It' [1.0]
            VVBD -> 'was' [1.0]
            VADJP -> VJJ [1.0]
            VJJ -> 'scary' [1.0]
        """

        survivor_quote_abstract_fact = None

        survivor_quote_grammar_2 = """
            S -> S2 NP VP [1.0]
            
            S2 -> NP2 VP2 [1.0]
            NP -> NDT NNN [1.0]
            VP -> VVBD [1.0]
            
            NDT -> 'a' [1.0]
            NNN -> 'witness' [1.0]
            NP2 -> NPRP [1.0]
            VP2 -> VVBD2 VADVP VVP [1.0]
            VVBD -> 'said' [1.0]
            
            NPRP -> 'we' [1.0]
            VVBD2 -> 'were' [1.0]
            VADVP -> VRB [1.0]
            VVP -> VVBG S3 [1.0]
            
            VRB -> 'just' [1.0]
            VVBG -> 'trying' [1.0]
            S3 -> VP3 [1.0]
            
            VP3 -> VTO VVP2 [1.0]
            VTO -> 'to' [1.0]
            VVP2 -> VVB VPP [1.0]
            
            VVB -> 'get' [1.0]
            VPP -> VIN VNP [1.0]
            
            VIN -> 'to' [1.0]
            VNP -> VNN [1.0]
            VNN -> 'safety,"' [1.0]
        """

        survivor_quote_abstract_fact_2 = Fact(
            subj=Person(kind=self.morphy('witness', 'noun')),
            event=Event(kind=self.morphy('said', 'verb'))
        )

        self.grammar = [survivor_quote_grammar, survivor_quote_grammar_2]
        self.abstract_fact = [survivor_quote_abstract_fact, survivor_quote_abstract_fact_2]
        self.last_quote = """
            We didn't know where the shots were coming from. So we just ran to try to get to safety and then we fell, and we were just trying to get to safety because everyone was running and screaming.
        """
