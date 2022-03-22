from Attributes.Attribute import Attribute
import nltk


class NationalityAttribute(Attribute):
    """
    Attribute that outputs nationality attribute
    """

    def __init__(self, ):
        super().__init__()
        self.pattern = '[NATIONALITY]'
        self.nationality = {}
        # words to ignore
        self.__ignore_words = ['islamist', 'sunni', 'kurdish', 'catholic', 'western', 'republican', 'democrat',
                               'democratic', 'shiite', 'muslim', 'non-muslim', 'islamic', 'christian', 'instagram',
                               'basque', 'buddhist', 'pro-russian', 'communist', 'southern']

    def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
        # to remove repetitive selection of NORP entity
        if self.nationality:
            return self.nationality

        nationality = {k: v for k, v in named_entities_dist['NORP'].items() if
                       len(nltk.word_tokenize(k)) <= 2 and k.lower() not in self.__ignore_words and v >= 40}

        self.nationality = nationality
        return nationality
        # nationality = random.choices(list(self.nationality.keys()), weights=list(self.nationality.values()))[0]
