from Attributes.Attribute import Attribute
import re


class AgeAttribute(Attribute):
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
                        age_mod = age_mod.replace('year old', 'year-old')

                    age_match = re.match(r'\d+', age_mod)
                    if age_match:
                        age = int(age_match.group(0)) if age_match.group(0).isnumeric() else -1
                        if age <= 15 or age >= 60:
                            continue

                    age_map[(age_mod, noun)] = noun_mod_occurrences[(mod, noun)]

        if not age_map:
            age_map[('20-year-old', obj_lemma)] = 1
            age_map[('25-year-old', obj_lemma)] = 1
            age_map[('30-year-old', obj_lemma)] = 1
        return age_map
