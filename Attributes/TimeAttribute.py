from Attributes.Attribute import Attribute

class TimeAttribute(Attribute):
    """
    Attribute that outputs time attribute
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[TIME]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        return named_entities_dist['TIME']
