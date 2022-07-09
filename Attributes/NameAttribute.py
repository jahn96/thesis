from Attributes.Attribute import Attribute
import nltk


class NameAttribute(Attribute):
    """
    Attribute that outputs name attribute
    """

    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[NAME]'
        self.first_names = {}
        self.last_names = {}

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        # to remove repetitive selection of PERSON entity
        if self.first_names and self.last_names:
            return self.first_names, self.last_names

        first_names = {}
        last_names = {}
        for k, v in named_entities_dist['PERSON'].items():
            names = nltk.word_tokenize(k)
            if len(names) == 2 and names[0][0].isupper() and names[1][0].isupper() and v >= 40:
                first_name, last_name = names
                first_names[first_name] = first_names.get(first_name, 0) + v
                last_names[last_name] = last_names.get(last_name, 0) + v

        self.first_names = first_names
        self.last_names = last_names

        return first_names, last_names

