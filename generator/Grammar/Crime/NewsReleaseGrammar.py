from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Modifier import Modifier
from Fact_tree.Multiple import Multiple
from Fact_tree.Object import Object
from Fact_tree.Person import Person
from Fact_tree.Phrase import Phrase
from generator.Grammar.Grammar import Grammar


class NewsReleaseGrammar(Grammar):
    """
    Grammar that outputs news media release
    """

    def __init__(self, tense, grammar_type, metadata):
        super().__init__(tense, grammar_type, metadata)

    def define_grammar(self):
        event = self.metadata['event']

        if event != 'shooting':
            self.grammar = ''
            self.abstract_fact = None
            return
        news_release_grammar = """
            S -> SBAR COMMA NP VP [1.0]
            
            SBAR -> IN S2 [1.0]
            COMMA -> ',' [1.0]
            NP -> NDT NNN NNN2 [1.0]
            VP -> VVBD [1.0]
            
            IN -> '"As' [1.0]
            S2 -> NP2 VP2 [1.0]
            NDT -> 'the' [1.0]
            NNN -> 'news' [1.0]
            NNN2 -> 'release' [1.0]
            VVBD -> 'said' [1.0]
            
            NP2 -> NQP NNNS [1.0]
            VP2 -> VVBD2 VVP [1.0]
            
            NQP -> NJJ NIN NCD [1.0]
            NNNS -> 'rounds' [1.0]
            VVBD2 -> 'were' [1.0]
            VVP -> VVBN VADVP COMMA S3 [1.0]
            
            NJJ -> 'many' [1.0]
            NIN -> 'as' [1.0]
            NCD -> '10' [1.0]
            VVBN -> 'fired' [1.0]
            VADVP -> VRB [1.0]
            S3 -> VP3 [1.0]
            
            VRB -> 'inside' [1.0]
            VP3 -> VVP2 [1.0]
            
            VVP2 -> VVBG VNP S4 [1.0]
            
            VVBG -> 'prompting' [1.0]
            VNP -> VDT VNNS [1.0]
            S4 -> VP4 [1.0]
            
            VDT -> 'some' [1.0]
            VNNS -> 'people' [1.0]
            VP4 -> VTO VVP4 [1.0]
            
            VTO -> 'to' [1.0]
            VVP4 -> VVB VPRT VNP5 [1.0]
            
            VVB -> 'jump' [1.0]
            VPRT -> VRP [1.0]
            VNP5 -> VDT2 VNNS5 [1.0]
            
            VRP -> 'out' [1.0]
            VDT2 -> 'the' [1.0]
            VNNS5 -> 'windows."' [1.0]
        """

        # "As many as 10 rounds were fired inside, prompting some people to jump out the windows.", the news release said.
        news_release_abstract_fact = Fact(
            subj=Person(kind='news release'),
            event=Event(kind=self.morphy('said', 'verb')),
            obj=Fact(
                subj=Object(kind=self.morphy('rounds', 'noun'), attrs={'count': Object(kind='10', attrs={'obj_mod': 'as many as'})}),
                event=Event(kind=self.morphy('fired', 'verb'),
                            passive=True,
                            attrs={'event_mod': 'inside', 'clause_part': Fact(
                                subj=Object(kind=self.morphy('rounds', 'noun')),
                                event=Event(kind=self.morphy('prompting', 'verb'),
                                            attrs={
                                                'obj': Person(kind=self.morphy('people', 'noun'),
                                                              attrs={'count': 'some'}),
                                                'phrase_mod': Phrase(kind='to', attrs={
                                                    'event': Event(kind=self.morphy('jump', 'verb') + ' out',
                                                                   attrs={'obj': Object(
                                                                       kind=self.morphy('windows', 'noun'))})
                                                })
                                            })
                            )})
            )
        )
        """
        'clause_part': Fact(
                                                       subj=Object(kind=self.morphy(self.__obj, 'noun')),
                                                       event=Event(kind=self.morphy('wearing', 'verb'),
                                                                   attrs={
                                                                          'obj': self.morphy('jacket', 'noun'),
                                                                          'phrase_mod': Phrase(kind='with', attrs={'obj': Multiple(conj='and', nodes=[
                                                                              Object(kind=self.morphy('jeans', 'noun'),
                                                                                     attrs={'obj_mod': Attribute()}),
                                                                              Object(kind=self.morphy('shoes', 'noun'),
                                                                                     attrs={
                                                                                         'obj_mod': Attribute()})
                                                                          ])})}),
                                                       obj=Object(kind=self.morphy('jacket', 'noun'), attrs={
                                                           'obj_mod': Attribute(),
        """
        self.grammar = news_release_grammar
        self.abstract_fact = news_release_abstract_fact
