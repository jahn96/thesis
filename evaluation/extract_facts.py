import spacy
from spacy.tokens.doc import Doc


def preprocess_summary(summary: str):
    return summary.replace('<n>', ' ')

def extract_facts(summary: Doc):
    """

    :param summary: preprocessed_summary document
    :return: list of facts – facts are list of (obj_mod and obj) or count and obj or (subj, verb, obj)
    """
    for tok in summary:

    pass


if __name__ == '__main__':
    nlp = spacy.load('en_core_web_sm')
    # TODO: make sure the age is connected with hyphen (32-year-old) or 32 years old
    # TODO: clock should be pm (am) or p.m (a.m) (if it appears) in the middle of sentence
    summary = """A 32-year-old female victim got knifepointed by 3 men at a best restaurant in haiti at 9:12 a.m. on Monday.<n>The first man had no description. The second man was described as about 22-year old.<n>The third man was described as about 30-year old."""

    # preprocess_summary
    preprocessed_summ = preprocess_summary(summary)
    doc = nlp(preprocessed_summ)

    print(type(doc))

