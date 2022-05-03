from nltk.stem import WordNetLemmatizer


class Attribute:
    """
    Attribute class that outputs the attribute of an object
    """
    def __init__(self, get_prev=False):
        self.__pattern = "[OBJ_MOD]"
        self.lemmatizer = WordNetLemmatizer()
        # a few words that would be ignored as its attribute either due to the difficulty of
        # extracting these from summary using Spacy or due to the awkwardness
        self.ignore_words = {'restaurant': ['own', 'physical', 'underground', 'permanent', 'domestic', 'actual', 'adjacent', 'more', 'chic', 'More', 'Somalia-based', '844-foot-high', 'high', 'finest', 'fine', 'little', 'shuttered', 'first', 'great', 'favorite', 'locavore', 'seafront', 'upscale', 'several', 'nearby', 'many', 'temporary', 'best', 'bloated'],
                             'bar': ['whimsical', 'little', 'publicized', 'fewer', 'more', 'child-proof', 'empty', 'horizontal', 'legal', 'tiny', 'numerous', 'own', 'wet', 'certain', 'normal', 'extra', 'worth', 'long', 'dive', 'adjacent', 'cool', 'marble-topped', 'different', 'fluorescent', 'light', 'official', 'independent', 'free', 'new', 'few', 'exclusive', 'a few', 'same', 'temporary', 'favorite', 'burglar', 'other', 'many', 'several', 'only', 'marble-topped', 'first', 'parallel', 'best', 'secret', 'uneven', 'even', 'last', 'high', 'low'],
                             'shoes': ['only', 'free', 'first', 'rarest', 'cool', 'great', 'good', 'best', 'unstructured', 'identical', 'blood shattered', 'certain', 'Italian', 'favorite', 'strong', 'high', 'own', 'waitress', 'same'],
                             'resort': ['Michael Jackson themed', 'same', 'expansive', 'Many', 'last', 'major', 'first', 'only', 'giant', 'small', 'many', 'several', 'main', 'other'],
                             'collar': ['relatable', 'electronic'],
                             'jean': ['usual'],
                             'jacket': ['undetonated'],
                             }

        self.get_prev = get_prev

    @property
    def pattern(self):
        return self.__pattern

    @pattern.setter
    def pattern(self, pattern):
        self.__pattern = pattern

    def generate_attr(self, obj: str, noun_mod_occurrences: dict, named_entities_dist: dict):
        objs = {}
        obj_lemma = self.lemmatizer.lemmatize(obj)

        for (mod, noun) in noun_mod_occurrences:
            if noun == obj_lemma and mod.lower() not in self.ignore_words.get(obj.lower(), []):
                new_mod = mod
                # connect compound attribute with a hyphen to be recognized as a single word with Spacy
                if len(mod.split()) == 2:
                    new_mod = mod.replace(' ', '-')

                if new_mod == 'inclusive':
                    new_mod = 'all-inclusive'
                objs[(new_mod, noun)] = noun_mod_occurrences[(mod, noun)]

        # if there is no attribute of an object in the realistic fact, then just output color attribute
        if not objs:
            objs = {'red': 1, 'blue': 1, 'black': 1}

        if obj == 'bar':
            objs[('cocktail', obj_lemma)] = 2

        if obj in ['collar', 'shoes', 'jeans']:
            objs[('red', obj_lemma)] = 1
            objs[('black', obj_lemma)] = 1
            objs[('pink', obj_lemma)] = 1

        # print(objs)
        return objs

