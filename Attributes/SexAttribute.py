from Attributes.Attribute import Attribute


class SexAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.pattern = '[SEX]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        sex = {}
        for (mod, noun) in noun_mod_occurrences:
            if noun == obj:
                if mod in ['female', 'male']:
                    sex[(mod, noun)] = noun_mod_occurrences[(mod, noun)]
        return sex
