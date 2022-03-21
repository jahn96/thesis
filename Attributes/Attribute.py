from nltk.stem import WordNetLemmatizer


class Attribute:
    def __init__(self):
        self.__pattern = "[OBJ_MOD]"
        self.lemmatizer = WordNetLemmatizer()
        self.ignore_words = {'restaurant': ['seafront'], 'shoes': ['blood shattered']}

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
            if noun == obj_lemma and mod not in self.ignore_words.get(obj, []):
                new_mod = mod
                if len(mod.strip()) == 2:
                    new_mod = mod.replace(' ', '-')
                objs[(new_mod, noun)] = noun_mod_occurrences[(mod, noun)]

        if not objs:
            objs = {'red': 1, 'blue': 1, 'black': 1}
        return objs

