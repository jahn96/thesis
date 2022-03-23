from Attributes.Attribute import Attribute


class EventAttribute(Attribute):
    """
    Attribute that outputs event attribute
    """

    def __init__(self):
        super().__init__()
        self.pattern = '[EVENT]'

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        # # TODO: get this event fact from mined_event
        event_attrs = {'mug': 1, 'knifepoint': 1}
        return event_attrs
