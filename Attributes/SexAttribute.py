from Attributes.Attribute import Attribute


class SexAttribute(Attribute):
    """
    Attribute that outputs sex attribute
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[SEX]'
        self.sex_fact = {}

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        if self.sex_fact:
            return self.sex_fact

        sex = {}
        for (mod, noun) in noun_mod_occurrences:
            if noun == obj:
                if mod in ['female', 'male']:
                    sex[(mod, noun)] = noun_mod_occurrences[(mod, noun)]

        self.sex_fact = sex

        return sex
