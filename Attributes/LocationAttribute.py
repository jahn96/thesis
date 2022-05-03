from Attributes.Attribute import Attribute


class LocationAttribute(Attribute):
    """
    Attribute that outputs location attribute
    """
    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[LOCATION]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        return named_entities_dist['GPE']

