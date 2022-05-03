import random

from Attributes.Attribute import Attribute


class YearAttribute(Attribute):
    """
    Attribute that outputs year attribute of an object
    """

    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[YEAR]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        objs = {}
        obj_lemma = self.lemmatizer.lemmatize(obj)

        for (mod, noun) in noun_mod_occurrences:
            if noun == obj_lemma and mod.isnumeric():
                objs[(mod, noun)] = noun_mod_occurrences[(mod, noun)]

        if not objs:
            year = random.choice(range(1980, 2010))
            objs = {(str(year), obj_lemma): 1}
        return objs
