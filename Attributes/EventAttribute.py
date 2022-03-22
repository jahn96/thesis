from Attributes.Attribute import Attribute


class EventAttribute(Attribute):
    """
    Attribute that outputs event attribute
    """

    def __init__(self):
        super().__init__()
        self.pattern = '[EVENT]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        # # TODO: get this event fact from mined_event
        event_attrs = {'mug': 1, 'knifepoint': 1}
        return event_attrs
