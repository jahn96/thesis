from Attributes.Attribute import Attribute
import re


class AgeAttribute(Attribute):
    """
    Attribute that outputs age attribute of an object
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[AGE]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        age_map = {}
        obj_lemma = self.lemmatizer.lemmatize(obj)
        for (mod, noun) in noun_mod_occurrences:
            if noun == obj_lemma:
                if re.match(r'.+ aged', mod) or re.match(r'\d+[-\s]year.{1,2}old', mod):
                    # if 'aged' in mod or 'year old' in mod:
                    age_mod = mod
                    if 'year old' in age_mod:
                        age_mod = age_mod.replace('year old', 'years old')

                    age_mod = age_mod.replace('-', ' ')
                    if re.search(r'year\s', age_mod):
                        age_mod = age_mod.replace('year', 'years')

                    age_match = re.match(r'\d+', age_mod)
                    if age_match:
                        age = int(age_match.group(0)) if age_match.group(0).isnumeric() else -1
                        # skip the ages that are too young or too old
                        if age <= 15 or age >= 60:
                            continue

                    age_map[(age_mod, noun)] = noun_mod_occurrences[(mod, noun)]

        # if there's no age of a given object in the realistic fact, then choose among 20, 25, and 30 years old
        if not age_map:
            age_map[('20 years old', obj_lemma)] = 1
            age_map[('25 years old', obj_lemma)] = 1
            age_map[('30 years old', obj_lemma)] = 1

        return age_map
