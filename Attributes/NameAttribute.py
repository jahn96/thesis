from Attributes.Attribute import Attribute
import nltk


class NameAttribute(Attribute):
    """
    Attribute that outputs name attribute
    """

    def __init__(self, get_prev=False):
        super().__init__(get_prev)
        self.pattern = '[NAME]'
        self.names_dict = {}

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        # to remove repetitive selection of PERSON entity
        if self.names_dict:
            return self.names_dict

        names_dict = {}
        for k, v in named_entities_dist['PERSON'].items():
            names = nltk.word_tokenize(k)
            if len(names) == 2 and names[0][0].isupper() and names[1][0].isupper() and v >= 40:
                name = ' '.join(names)
                names_dict[name] = names_dict.get(name, 0) + v

        self.names_dict = names_dict

        return names_dict
