from Attributes.Attribute import Attribute

class TimeAttribute(Attribute):
    """
    Attribute that outputs time attribute
    """
    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[TIME]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        return named_entities_dist['TIME']
