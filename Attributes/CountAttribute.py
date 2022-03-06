from Attributes.Attribute import Attribute


class CountAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.pattern = '[COUNT]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        objs = {}
        obj_lemma = self.lemmatizer.lemmatize(obj)

        for (mod, noun) in noun_mod_occurrences:
            if noun == obj_lemma and mod.isnumeric():
                objs[(mod, noun)] = noun_mod_occurrences[(mod, noun)]

        if not objs:
            objs = {}
        return objs