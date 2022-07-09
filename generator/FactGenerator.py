import nltk
import random
import re
import numpy as np

from Attributes.Attribute import Attribute
from Attributes.NameAttribute import NameAttribute
from Fact_tree.Fact import Fact
from nltk.corpus import cmudict  # >>> nltk.download('cmudict')

class FactGenerator:
    """
    Fact generator class
    """
    def __init__(self, named_entities_dist, noun_mod_occurrences):
        self.nationality_ignore_words = ['islamist', 'sunni', 'kurdish', 'catholic', 'western', 'republican',
                                         'democrat',
                                         'democratic', 'shiite', 'muslim', 'non-muslim', 'islamic', 'christian',
                                         'instagram', 'kurd',
                                         'basque', 'buddhist', 'pro-russian', 'communist', 'southern']
        self.NATIONALITY_THRESHOLD = 40

        self.gpe_ignore_words = ['Obama', 'Snowden', 'Twitter']
        self.GPE_COUNT_THRESHOLD = 100

        self.named_entities_dist = self.preprocess_named_entities_dist(named_entities_dist)
        self.noun_mod_occurrences = noun_mod_occurrences

        self.prev_fact = {}

    def generate_text(self, grammar: str, abstract_fact: Fact, fact_table):
        pass

    def get_correct_article(self, word):
        if self.starts_with_vowel_sound(word):
            return 'an'
        return 'a'

    def starts_with_vowel_sound(self, word, pronunciations=cmudict.dict()):
        for syllables in pronunciations.get(word.lower(), []):
            return syllables[0][-1].isdigit()

    def get_random_fact(self, fact_dict, num_fact):
        keys = []
        counts = []
        for k, v in fact_dict.items():
            keys.append(k)
            counts.append(v)

        weights = np.array(counts) / sum(counts)
        random_fact = random.choices(
            population=keys,
            weights=weights,
            k=num_fact
        )[0]
        return random_fact

    def generate_random_fact(self, obj: str, attr: Attribute, num_fact: int = 1, get_prev = False):
        """
      Params:
      fact_dict: dictionary of mined facts - pairs of facts and their occurrences

      Return:
      tuple of string - return random fact based on the weights of occurrences
    """
        if get_prev:
            return self.prev_fact[attr.pattern]

        if isinstance(attr, NameAttribute):
            first_names, last_names = self.get_fact(obj, attr)
            random_fact = self.get_random_fact(first_names, num_fact)
            random_fact += (' ' + self.get_random_fact(last_names, num_fact))
        else:
            fact_dict = self.get_fact(obj, attr)
            random_fact = self.get_random_fact(fact_dict, num_fact)

        if type(random_fact) == tuple:
            self.prev_fact[attr.pattern] = random_fact[0]
            return random_fact[0]

        self.prev_fact[attr.pattern] = random_fact
        return random_fact

    def preprocess_named_entities_dist(self, named_entities_dist):
        # preprocess
        preprocessed_named_entities_dist = {}

        for named_entity, value in named_entities_dist.items():
            preprocessed_named_entities_dist[named_entity] = {}

            for literal, count in value.items():
                literal = literal.replace("'", "")

                # nationality
                if named_entity == 'NORP' and literal[-1] == 's':
                    if len(nltk.word_tokenize(
                            literal)) > 2 or literal.lower() in self.nationality_ignore_words \
                            or count < self.NATIONALITY_THRESHOLD:
                        continue

                    new_literal = literal.rstrip('s')
                    if new_literal in preprocessed_named_entities_dist[named_entity]:
                        preprocessed_named_entities_dist[named_entity][new_literal] += count
                    else:
                        preprocessed_named_entities_dist[named_entity][new_literal] = count

                # location
                elif named_entity == 'GPE':
                    if count < self.GPE_COUNT_THRESHOLD:
                        continue

                    new_literal = re.sub(r"\s[a-z]+", "", literal)

                    if re.search(r'\d', new_literal) or len(new_literal.split()) > 2 or new_literal in self.gpe_ignore_words:
                        continue

                    if len(new_literal.split()) == 1 and 'U.S.'.lower() not in new_literal.lower() and 'D.C.'.lower() not in new_literal.lower():
                        new_literal = new_literal.capitalize()

                    if new_literal == 'U.S.':
                        new_literal = 'the U.S.'

                    if new_literal in preprocessed_named_entities_dist[named_entity]:
                        preprocessed_named_entities_dist[named_entity][new_literal] += count
                    else:
                        preprocessed_named_entities_dist[named_entity][new_literal] = count

                # time
                elif named_entity == 'TIME':
                    if self.filter_time(literal):
                        preprocessed_named_entities_dist[named_entity][literal] = count
                else:
                    preprocessed_named_entities_dist[named_entity][literal] = count

        return preprocessed_named_entities_dist

    def filter_time(self, time_str):
        ignore_times = ['30 p.m.']
        time_match = re.match(r'^(\d:\d\d|\d+) ([APap]\.[mM]\.$)', time_str)
        if time_match:
            if time_match.group(0) not in ignore_times:
                time = time_match.group(1)
                pm_am = time_match.group(2)
                if ':' in time:
                    time = time.split(':')[0]

                # error checking
                if time.isnumeric():
                    time = int(time)
                else:
                    time = -1

                # if time is between 6am and 6pm, ignore
                if time == -1 or ((time < 6 or time >= 12) and 'p' in pm_am.lower()) or \
                        ((time > 6 or time < 12) and 'a' in pm_am.lower()):
                    return False
                else:
                    return True
        return False

    def get_fact(self, obj: str, attr: Attribute):
        return attr.generate_attr(obj, self.noun_mod_occurrences, self.named_entities_dist)

    def fill_grammar_w_fact(self, grammar: str, pattern: str, fact: str) -> str:
        if type(fact) is tuple:
            fact = fact[0]
        escaped_pattern = f"""\{pattern[:-1]}\{pattern[-1]}"""
        filled_grammar = re.sub(escaped_pattern, fact, grammar, 1)
        return filled_grammar
