from typing import List, Tuple, Union
import nltk
from nltk.parse.generate import generate

from Attributes.Attribute import Attribute
from Fact_tree.Fact import Fact
from Fact_tree.Node import Node
from generator.FactGenerator import FactGenerator


class CrimeFactGenerator(FactGenerator):
    def __init__(self, named_entities_dist, noun_mod_occurrences):
        super().__init__(named_entities_dist, noun_mod_occurrences)

    def generate_data(self, grammar: str, abstract_fact: Fact, data, fact_table):
        # check duplicate
        while True:
            new_table_entry = []

            # fill grammar with fact
            grammar = self.traverse_fact(grammar, abstract_fact, new_table_entry)

            pcfg_grammar = nltk.PCFG.fromstring(grammar)

            if new_table_entry not in fact_table:
                fact_table.extend(new_table_entry)
                for sent in generate(pcfg_grammar, n=1):
                    temp = ' '.join(sent)

                    datum = temp[0].upper() + temp[1:] + '.'
                    data.append(datum)
                break

    # TODO: verb should be stored with subject and object
    # TODO: subject and object should be stored with its attributes
    def traverse_fact(self, grammar: str, fact: Union[Fact, Node, list], fact_table: List, is_phrase_mod: bool = False):
        """
        Traverse fact, get facts, and fill facts
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
            grammar = self.traverse_fact(grammar, fact.subj, fact_table)
            grammar = self.traverse_fact(grammar, fact.event, fact_table)
            grammar = self.traverse_fact(grammar, fact.obj, fact_table)

        elif type(fact) == list:
            for el in fact:
                grammar = self.traverse_fact(grammar, el, fact_table)

        elif isinstance(fact, Node):
            attrs = fact.attrs if fact.attrs else {}
            fact_table_el = {}

            if fact.neg:
                fact_table_el['neg'] = fact.neg

            obj = fact.kind

            fact_table_el['kind'] = obj

            for attr, val in attrs.items():

                if type(val) == list:
                    for el in val:
                        grammar = self.traverse_fact(grammar, el, fact_table, attr == 'phrase_mod')

                    # phrase_mod list
                    if attr == 'phrase_mod':
                        phrase_mods = []

                        preps = [mod.kind for mod in val]

                        objs = [mod.__getattribute__('obj') if isinstance(mod, Node) else mod['obj'] for mod in val]

                        assert len(preps) == len(objs)

                        for i in range(len(preps)):
                            prep = preps[i]
                            obj = objs[i]

                            phrase_mods.append(prep + ' ' + obj)

                        setattr(fact, attr, phrase_mods)

                        fact_table_el[attr] = phrase_mods

                # clause_mod
                elif isinstance(val, Fact):
                    grammar = self.traverse_fact(grammar, val.subj, fact_table)
                    grammar = self.traverse_fact(grammar, val.event, fact_table)
                    grammar = self.traverse_fact(grammar, val.obj, fact_table)

                elif isinstance(val, Attribute):
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
                    if attr == 'phrase_mod':

                        grammar = self.traverse_fact(grammar, val, fact_table, True)

                        # obj = val.attrs['obj']
                        # phrase_mod = prep

                        prep = val.kind

                        # list
                        if type(val.attrs['obj']) == list:
                            objs = [obj.kind for obj in val.attrs['obj']]
                            phrase_mod = prep + ' ' + ','.join(objs)
                        # Node
                        elif isinstance(val.attrs['obj'], Node):
                            obj = val.attrs['obj'].kind
                            phrase_mod = prep + ' ' + obj
                        # Attribute
                        else:
                            obj = val.__getattribute__('obj')
                            phrase_mod = prep + ' ' + obj

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

        # {'kind': 'knifepointed', 'time': '2:15 a.m.', 'date': 'Tuesday night'}, {'kind': 'men', 'location': 'Colorado'}
        return grammar
