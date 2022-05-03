from typing import List, Union
import nltk
from nltk.parse.generate import generate

from Attributes.Attribute import Attribute
from Fact_tree.Clause import Clause
from Fact_tree.Event import Event
from Fact_tree.Fact import Fact
from Fact_tree.Multiple import Multiple
from Fact_tree.Node import Node
from generator.FactGenerator import FactGenerator


class CrimeFactGenerator(FactGenerator):
    """
    Generator that generates crime fact that would be used in grammar to generate a crime article
    """

    def __init__(self, named_entities_dist, noun_mod_occurrences):
        super().__init__(named_entities_dist, noun_mod_occurrences)

    def generate_text(self, grammar: str, abstract_fact: Fact, fact_table):
        # check duplicate
        while True:
            new_table_entry = []

            # fill grammar with the realistic fact
            grammar = self.traverse_fact(grammar, abstract_fact, new_table_entry)

            pcfg_grammar = nltk.PCFG.fromstring(grammar)

            if new_table_entry not in fact_table:
                fact_table.extend(new_table_entry)
                for sent in generate(pcfg_grammar, n=1):
                    # replace article with correct article
                    article_tok = '[ARTICLE]'

                    for i in range(len(sent) - 1):
                        tok = sent[i]
                        if article_tok in tok:
                            noun = sent[i + 1]
                            corr_article = self.get_correct_article(noun)
                            sent[i] = tok.replace(article_tok, corr_article)

                    temp = ' '.join(sent)

                    text = temp[0].upper() + temp[1:]
                    if text[-1] not in ['"', ',']:
                        text += '.'

                    text = text.replace(" ,", ",")
                    text = text.replace(" .", ".")
                    text = text.replace(" '", "'")

                    return text

    def traverse_fact_node(self, grammar: str, fact: Fact, fact_table: List):
        """

        :param grammar:
        :param fact:
        :param fact_table:
        :return:
        """
        grammar = self.traverse_fact(grammar, fact.subj, fact_table)
        grammar = self.traverse_fact(grammar, fact.obj, fact_table)

        meta_data = {}
        # passing down subject and object to its verb
        if fact.subj:
            if isinstance(fact.subj, Multiple):
                subjs = []
                for node in fact.subj.nodes:
                    subjs.append(node.kind)
                conj = ' ' + fact.subj.conj + ' '
                meta_data['subj'] = conj.join(subjs)
            else:
                meta_data['subj'] = fact.subj.kind

        if fact.obj:
            if isinstance(fact.obj, Multiple):
                objs = []
                for node in fact.obj.nodes:
                    objs.append(node.kind)
                conj = ' ' + fact.obj.conj + ' '
                meta_data['obj'] = conj.join(objs)
            elif isinstance(fact.obj, Fact):
                if fact.obj.subj:
                    if isinstance(fact.obj.subj, Multiple):
                        subjs = []
                        for node in fact.obj.subj.nodes:
                            subjs.append(node.kind)
                        conj = ' ' + fact.obj.subj.conj + ' '
                        meta_data['obj'] = conj.join(subjs)
                    else:
                        meta_data['obj'] = fact.obj.subj.kind
            else:
                meta_data['obj'] = fact.obj.kind

        grammar = self.traverse_fact(grammar, fact.event, fact_table, meta_data=meta_data)

        if isinstance(fact.event, Multiple):
            if not isinstance(fact.event.nodes[0], Fact):
                event_kind = (' ' + fact.event.conj + ' ').join(node.kind for node in fact.event.nodes)
                meta_data['kind'] = event_kind
        else:
            if fact.event:
                meta_data['kind'] = fact.event.kind

        return grammar, meta_data

    def repr_prep_adv_clause_helper(self, pos_node):
        phrase_mod = ''
        if pos_node:
            if isinstance(pos_node, Multiple):
                kinds = [node.kind for node in pos_node.nodes]
                conj = ' ' + pos_node.conj + ' '
                kinds = conj.join(kinds)
                phrase_mod += (' ' + kinds)
            else:
                kind = pos_node.kind
                phrase_mod += (' ' + kind)
        return phrase_mod

    def repr_prep_adv_clause(self, clause_adv: Clause):
        connective = clause_adv.connective
        phrase_mod = connective

        phrase_mod += (self.repr_prep_adv_clause_helper(clause_adv.subj))
        phrase_mod += (self.repr_prep_adv_clause_helper(clause_adv.event))
        phrase_mod += (self.repr_prep_adv_clause_helper(clause_adv.obj))

        return phrase_mod

    # TODO: verb should be stored with subject and object
    # TODO: subject and object should be stored with its attributes
    def traverse_fact(self, grammar: str, fact: Union[Multiple, Fact, Node, list], fact_table: List,
                      is_phrase_mod: bool = False,
                      meta_data: dict = None):
        """
        Traverse fact, get facts, and fill facts
        :param meta_data:
        :param is_phrase_mod:
        :param metadata:
        :param fact_table:
        :param grammar:
        :param fact:
        :return:
        """
        if not fact:
            return grammar

        if isinstance(fact, Fact):
            grammar, _ = self.traverse_fact_node(grammar, fact, fact_table)

        # elif isinstance(fact, Multiple):
        #     # fact_table_el = meta_data if meta_data else {}
        #     # if fact.attrs:
        #     #     conj = fact.conj
        #     #     nodes = [node.kind for node in fact.nodes]
        #     #     obj = conj.join(nodes)
        #     #
        #     #     fact_table_el['kind'] = obj
        #     #
        #     #     for attr in fact.attrs:
        #     #
        #     #     fact_table_el[]
        #     #
        #     #     # f
        #         # not is_phrase_mod and len(fact_table_el) > 1:
        #         # fact_table.append({repr(fact): fact_table_el})
        #
        #     for el in fact.nodes:
        #         grammar = self.traverse_fact(grammar, el, fact_table)
        #     print(fact_table)
        elif isinstance(fact, Multiple):
            for el in fact.nodes:
                if isinstance(el, Fact):
                    grammar, _ = self.traverse_fact_node(grammar, el, fact_table)
                else:
                    grammar = self.traverse_fact(grammar, el, fact_table, meta_data=meta_data)

        elif isinstance(fact, Node):
            attrs = fact.attrs if fact.attrs else {}
            fact_table_el = meta_data.copy() if meta_data else {}

            if hasattr(fact, 'neg') and fact.neg:
                fact_table_el['neg'] = fact.neg

            # add passive
            if isinstance(fact, Event) and fact.passive:
                fact_table_el['passive'] = fact.passive

            obj = fact.kind

            # if isinstance(obj, Attribute):
            #     # get fact
            #     random_fact = self.generate_random_fact(fact.attrs['kind'], obj)
            #
            #     # update fact
            #     setattr(fact, 'kind', random_fact)
            #
            #     # get pattern
            #     attr_pattern = obj.pattern
            #
            #     # fill fact
            #     grammar = self.fill_grammar_w_fact(grammar, attr_pattern, random_fact)
            #
            #     # make obj as a random fact
            #     obj = random_fact

            fact_table_el['kind'] = obj

            for attr, val in attrs.items():
                if not val:
                    continue

                if isinstance(val, Multiple):
                    for node in val.nodes:
                        grammar = self.traverse_fact(grammar, node, fact_table, 'phrase_mod' in attr)

                    # phrase_mod is multiple
                    if 'phrase_mod' in attr:
                        phrase_mods = []

                        preps = [node.kind for node in val.nodes]

                        objs = [node.__getattribute__('obj') if isinstance(node, Node) else node for node in val.nodes]

                        assert len(preps) == len(objs)

                        for i in range(len(preps)):
                            prep = preps[i]
                            obj = objs[i]

                            phrase_mods.append(prep + ' ' + obj)

                        setattr(fact, attr, phrase_mods)

                        fact_table_el[attr] = phrase_mods

                    elif attr == 'event_mod':
                        # Multiple(conj='and', nodes=[Modifier(kind='dead'), Modifier(kind='wounded')]
                        objs = [obj.kind for obj in val.nodes]
                        conj = ' ' + val.conj + ' '
                        event_mod = conj.join(objs)
                        setattr(fact, attr, event_mod)
                        fact_table_el[attr] = event_mod

                # clause_adv
                elif isinstance(val, Clause):
                    # Add relationship between main clause and subordinate clause For example: The arrest came after
                    # police responded Tuesday (after relationship between (arrest came) and (police responded)
                    connective = val.connective

                    grammar, sub_meta_data = self.traverse_fact_node(grammar, val, fact_table)

                    # TODO: change it to string depending on fact extraction
                    sub_ordinate = connective

                    # Add subordinate
                    if 'subj' in sub_meta_data:
                        sub_ordinate += ' ' + sub_meta_data['subj']

                    if 'kind' in sub_meta_data:
                        sub_ordinate += ' ' + sub_meta_data['kind']

                    # if 'passive' in sub_meta_data:
                    #     sub_ordinate['sub_passive'] = sub_meta_data['passive']
                    #
                    # if 'neg' in sub_meta_data:
                    #     sub_ordinate['sub_neg'] = sub_meta_data['neg']

                    fact_table_el['sub_ord'] = sub_ordinate

                elif isinstance(val, Fact):
                    grammar, _ = self.traverse_fact_node(grammar, val, fact_table)

                elif isinstance(val, Attribute):
                    if val.get_prev:
                        random_fact = self.prev_fact[val.pattern]
                    else:
                        # get fact
                        random_fact = self.generate_random_fact(obj, val)

                    # update fact
                    setattr(fact, attr, random_fact)

                    # fill table element
                    fact_table_el[attr] = random_fact

                    # get pattern
                    attr_pattern = val.pattern

                    # fill fact
                    grammar = self.fill_grammar_w_fact(grammar, attr_pattern, random_fact)

                # phrase_mod
                elif isinstance(val, Node):
                    if 'phrase_mod' in attr:

                        # value of phrase mod should have 'obj', 'clause_adv', or 'event' as its attribute
                        assert 'obj' in val.attrs or 'clause_adv' in val.attrs or 'event' in val.attrs

                        grammar = self.traverse_fact(grammar, val, fact_table, True)

                        prep = val.kind

                        # preposition + noun
                        if 'obj' in val.attrs:
                            # Multiple
                            if isinstance(val.attrs['obj'], Multiple):
                                objs = [obj.kind for obj in val.attrs['obj'].nodes]
                                conj = ' ' + val.attrs['obj'].conj + ' '
                                phrase_mod = prep + ' ' + conj.join(objs)
                            # Node
                            elif isinstance(val.attrs['obj'], Node):
                                obj = val.attrs['obj'].kind
                                phrase_mod = prep + ' ' + obj
                            # Attribute
                            else:
                                obj = val.__getattribute__('obj')
                                phrase_mod = prep + ' ' + obj

                        # preposition + adverbial clause
                        elif 'clause_adv' in val.attrs:
                            # TODO: check this - need to be dictionary

                            if isinstance(val.attrs['clause_adv'], Multiple):
                                conj = val.attrs['clause_adv'].conj
                                nodes = val.attrs['clause_adv'].nodes
                                phrase_mod = prep + ' ' + conj.join([self.repr_prep_adv_clause(node) for node in nodes])
                                pass
                            else:
                                # representation: prep connective subjs verbs objs
                                phrase_mod = prep + ' ' + self.repr_prep_adv_clause(val.attrs['clause_adv'])

                        # preposition + verb
                        else:
                            # Multiple
                            if isinstance(val.attrs['event'], Multiple):
                                events = [event.kind for event in val.attrs['event'].nodes]
                                conj = ' ' + val.attrs['event'].conj + ' '
                                phrase_mod = prep + ' ' + conj.join(events)
                            # Node
                            elif isinstance(val.attrs['event'], Node):
                                event = val.attrs['event'].kind
                                phrase_mod = prep + ' ' + event
                            # Attribute
                            else:
                                event = val.__getattribute__('event')
                                phrase_mod = prep + ' ' + event

                        setattr(fact, attr, phrase_mod)

                        fact_table_el[attr] = phrase_mod
                    else:
                        setattr(fact, attr, val.kind)

                        # empty kind
                        empty_kind = True if not val.kind else False

                        fact_table_el[attr] = val.kind

                        grammar = self.traverse_fact(grammar, val, fact_table)

                        if empty_kind:
                            fact_table_el[attr] = val.kind
                else:
                    # just string
                    setattr(fact, attr, val)

                    # fill table element
                    fact_table_el[attr] = val

                # reset attributes to update
                # fact.attrs = None

            # if value is a phrase modifier or fact_table_el has only one key (kind), skip
            if not is_phrase_mod and len(fact_table_el) > 1:
                fact_table.append({repr(fact): fact_table_el})

        return grammar
