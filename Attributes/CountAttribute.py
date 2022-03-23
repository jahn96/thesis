from Attributes.Attribute import Attribute


class CountAttribute(Attribute):
    """
    Attribute that outputs count attribute of an object
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[COUNT]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        objs = {}
        obj_lemma = self.lemmatizer.lemmatize(obj)

        for (mod, noun) in noun_mod_occurrences:
            if noun == obj_lemma and mod.isnumeric():
                objs[(mod, noun)] = noun_mod_occurrences[(mod, noun)]

        return objs