from Attributes.Attribute import Attribute
import nltk


class NameAttribute(Attribute):
    def __init__(self, ):
        super().__init__()
        self.pattern = '[NAME]'

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        names_dict = {}
        for k, v in named_entities_dist['PERSON'].items():
            names = nltk.word_tokenize(k)
            if len(names) == 2 and names[0][0].isupper() and names[1][0].isupper() and v >= 40:
                name = ' '.join(names)
                names_dict[name] = names_dict.get(name, 0) + v
        return names_dict
