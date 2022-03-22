from Attributes.Attribute import Attribute


class LocationAttribute(Attribute):
    """
    Attribute that outputs location attribute
    """
    def __init__(self):
        super().__init__()
        self.pattern = '[LOCATION]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        return named_entities_dist['GPE']

