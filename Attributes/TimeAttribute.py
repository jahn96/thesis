from Attributes.Attribute import Attribute

class TimeAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.pattern = '[TIME]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        return named_entities_dist['TIME']
