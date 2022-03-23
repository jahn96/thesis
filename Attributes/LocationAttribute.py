from Attributes.Attribute import Attribute


class LocationAttribute(Attribute):
    """
    Attribute that outputs location attribute
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[LOCATION]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        return named_entities_dist['GPE']

