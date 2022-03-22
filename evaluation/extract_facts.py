import spacy
from spacy.tokens.doc import Doc
# from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
import nltk

from evaluation.utils import update_tokenizer

ignore_phrases = ["the US state of "]

def preprocess_summary(summary: str):
    for ignore_phrase in ignore_phrases:
      summary = summary.replace(ignore_phrase, '')
    return summary.replace('<n>', ' ')


def extract_facts_from_summary(summary, nlp, stemmer, lemmatizer):
    noun_modifiers = {}
    obj_counter = {}
    subj_verb = {}
    verb_obj = {}
    noun_neg = {}
    event_neg = {}
    event_modifiers = {}

    count_num_map = {
        'one': 1,
        'two': 2,
        'three': 3
    }

    preprocessed_summ = preprocess_summary(summary.strip())
    doc = nlp(preprocessed_summ)
    doc = update_tokenizer(doc)

    for tok in doc:

        # modifier
        if tok.dep_ == 'amod' and tok.head.pos_ in ['NOUN', 'PROPN']:
            # modifier and object
            noun = tok.head.text
            noun = lemmatizer.lemmatize(noun)
            modifier = tok.text
            if noun in noun_modifiers:
                noun_modifiers[noun].append([modifier, False])
            else:
                noun_modifiers[noun] = [[modifier, False]]

        # appos modifier
        if tok.dep_ == 'appos':  # and tok.pos_ == 'NUM':
            noun = tok.head.text
            noun = lemmatizer.lemmatize(noun)
            modifier = tok.text
            if noun in noun_modifiers:
                noun_modifiers[noun].append([modifier, False])
            else:
                noun_modifiers[noun] = [[modifier, False]]

        # clausal modifier of noun
        elif tok.dep_ == 'acl' and tok.pos_ == 'VERB':
            noun = tok.head.text
            noun = lemmatizer.lemmatize(noun)
            modifier = tok.text
            verb = stemmer.stem(modifier)
            if verb in subj_verb:
                subj_verb[verb].append([noun, False])
            else:
                subj_verb[verb] = [[noun, False]]

        # possessive modifier of noun
        elif tok.dep_ == 'poss' and tok.head.pos_ == 'NOUN':
            noun = lemmatizer.lemmatize(tok.head.text)
            possessive = tok.text

            if noun in noun_modifiers:
                noun_modifiers[noun].append([possessive, False])
            else:
                noun_modifiers[noun] = [[possessive, False]]

        # noun modifier with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ in ['NOUN', 'PROPN'] and tok.head.dep_ == 'pobj':
            if tok.head.head.dep_ == 'prep':
                if tok.head.head.head.pos_ == 'NOUN':
                    noun = tok.head.head.head.text
                    noun = lemmatizer.lemmatize(noun)
                    prep = tok.head.head.text
                    head_modifier = prep + ' ' + tok.head.text

                    # modifier = tok.head.head.text + ' ' + tok.text
                    if noun in noun_modifiers:
                        idx = noun_modifiers[noun].index([head_modifier, False])
                        # conj = ''

                        # for i in range(tok.i - 1, -1, -1):
                        #   if doc[i].pos_ == 'CCONJ':
                        #     conj = doc[i].text
                        #     break

                        noun_modifiers[noun][idx][0] += (',' + lemmatizer.lemmatize(tok.text))
                    else:
                        print('Warning: check conjunction!')
                elif tok.head.head.head.pos_ == 'VERB':
                    verb = tok.head.head.head.text
                    verb_stem = stemmer.stem(verb)
                    prep = tok.head.head.text
                    head_modifier = prep + ' ' + tok.head.text

                    # modifier = tok.head.head.text + ' ' + tok.text
                    if verb_stem in event_modifiers:
                        idx = event_modifiers[verb_stem].index([head_modifier, False])
                        # conj = ''

                        # for i in range(tok.i - 1, -1, -1):
                        #   if doc[i].pos_ == 'CCONJ':
                        #     conj = doc[i].text
                        #     break

                        event_modifiers[verb_stem][idx][0] += (',' + tok.text)
                    else:
                        print('Warning: check conjunction!')
            elif tok.head.head.dep_ == 'agent':
                verb = tok.head.head.head.text
                verb_stem = stemmer.stem(verb)
                head_noun = tok.head.text

                # modifier = tok.head.head.text + ' ' + tok.text
                if verb_stem in verb_obj:
                    idx = verb_obj[verb_stem].index([head_noun, False])

                    verb_obj[verb_stem][idx][0] += (',' + lemmatizer.lemmatize(tok.text))
                else:
                    print('Warning: check conjunction!')


        # noun with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ == 'NOUN':
            head_noun = tok.head.text
            head_noun = lemmatizer.lemmatize(head_noun)
            head_verb = tok.head.head.text
            head_verb_stem = stemmer.stem(head_verb)
            noun = tok.text
            noun = lemmatizer.lemmatize(noun)

            if head_noun in noun_modifiers:
                noun_modifiers[noun] = noun_modifiers[head_noun]

            if head_verb_stem in subj_verb:
                subj_verb[head_verb_stem].append([noun, False])

            if head_verb_stem in verb_obj:
                verb_obj[head_verb_stem].append([noun, False])

        # verb with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ == 'VERB':
            head_verb = tok.head.text
            verb = tok.text

            head_verb_stem = stemmer.stem(head_verb)
            verb_stem = stemmer.stem(verb)

            if head_verb_stem in subj_verb:
                subj_verb[verb_stem] = subj_verb[head_verb_stem]

            if head_verb_stem in verb_obj:
                verb_obj[verb_stem] = verb_obj[head_verb_stem]

            if head_verb_stem in event_modifiers:
                event_modifiers[verb_stem] = event_modifiers[head_verb_stem]

            if head_verb_stem in event_neg:
                event_neg[verb_stem] = event_neg[head_verb_stem]

                # relative clause (recl)
        elif tok.dep_ == 'relcl':
            if tok.pos_ == 'VERB':
                verb = tok.text
                verb_stem = stemmer.stem(verb)
                noun = tok.head.text
                noun = lemmatizer.lemmatize(noun)
                if verb_stem in subj_verb:
                    subj_verb[verb_stem].append([noun, False])
                else:
                    subj_verb[verb_stem] = [[noun, False]]

                # check another noun connected with conjunction
                nouns = []
                for i in range(tok.head.i + 1, tok.i):
                    curr_tok = doc[i]
                    if curr_tok.dep_ == 'conj' and curr_tok.pos_ == 'NOUN' and curr_tok.head.text == noun:
                        nouns.append([lemmatizer.lemmatize(curr_tok.text), False])

                for noun in nouns:
                    if verb_stem in subj_verb:
                        subj_verb[verb_stem].append(noun)
                    else:
                        subj_verb[verb_stem] = [noun]

        # verb + 'as' modifier
        elif tok.dep_ == 'amod' and tok.head.text == 'as':
            obj = tok.head.head
            modifier = tok.text
            if obj.pos_ == 'VERB':
                verb = obj.text
                verb_stem = stemmer.stem(verb)
                preposition = tok.head.text

                if verb_stem in event_modifiers:
                    event_modifiers[verb_stem].append([preposition + ' ' + modifier, False])
                else:
                    event_modifiers[verb_stem] = [[preposition + ' ' + modifier, False]]
            elif obj.pos_ == 'NOUN':
                noun = obj.text
                noun = lemmatizer.lemmatize(noun)
                if noun in noun_modifiers:
                    noun_modifiers[noun].append([modifier, False])
                else:
                    noun_modifiers[noun] = [[modifier, False]]

        # count
        elif tok.dep_ == 'nummod' and tok.head.pos_ == 'NOUN':
            noun = tok.head.text
            noun = lemmatizer.lemmatize(noun)
            if noun in obj_counter:
                num = int(tok.text) if tok.text.isnumeric() else count_num_map[tok.text.lower()]
                obj_counter[noun].append([num, False])
            else:
                num = int(tok.text) if tok.text.isnumeric() else count_num_map[tok.text.lower()]
                obj_counter[noun] = [[num, False]]

        # subj, verb, obj
        elif tok.dep_ in ['nsubjpass', 'nsubj']:
            # filter out relative clause verb
            if tok.head.dep_ != 'relcl':
                verb = tok.head.text
                verb_stem = stemmer.stem(verb)

                # add passive verb
                subj = tok.text
                subj = lemmatizer.lemmatize(subj)
                if verb_stem in subj_verb:
                    subj_verb[verb_stem].append([subj, False])
                else:
                    subj_verb[verb_stem] = [[subj, False]]

        # active obj
        elif tok.dep_ == 'dobj':
            verb = tok.head.text
            verb_stem = stemmer.stem(verb)
            obj = tok.text
            obj = lemmatizer.lemmatize(obj)
            if verb_stem in verb_obj:
                verb_obj[verb_stem].append([obj, False])
            else:
                verb_obj[verb_stem] = [[obj, False]]

        # preposition object (phrase modifier)
        elif tok.dep_ == 'pobj':
            # passive obj
            preposition = tok.head

            if preposition.dep_ == 'agent':
                verb = tok.head.head.text
                verb_stem = stemmer.stem(verb)
                if verb_stem in verb_obj:
                    verb_obj[verb_stem].append([tok.text, False])
                else:
                    verb_obj[verb_stem] = [[tok.text, False]]

            # location, place, time, ... modifiers
            else:
                # noun phrase modifier
                if tok.head.head.pos_ == 'NOUN':
                    noun = tok.head.head.text
                    noun = lemmatizer.lemmatize(noun)
                    phrase_mod = tok.head.text + ' ' + tok.text
                    if noun in noun_modifiers:
                        noun_modifiers[noun].append([phrase_mod, False])
                    else:
                        noun_modifiers[noun] = [[phrase_mod, False]]
                # verb phrase modifier
                elif tok.head.head.pos_ == 'VERB':
                    verb = tok.head.head.text
                    verb_stem = stemmer.stem(verb)
                    if preposition.text.lower() == 'as':
                        # get subj
                        subj = subj_verb[verb_stem][0]
                        if subj in noun_modifiers:
                            noun_modifiers[subj].append([tok.text, False])
                        else:
                            noun_modifiers[subj] = [[tok.text, False]]

                    else:
                        phrase_mod = preposition.text + ' ' + tok.text
                        if verb_stem in event_modifiers:
                            event_modifiers[verb_stem].append([phrase_mod, False])
                        else:
                            event_modifiers[verb_stem] = [[phrase_mod, False]]

        # adverbial clause modifier (advcl)
        elif tok.dep_ == 'advcl' and tok.pos_ == 'VERB':
            if tok.head.pos_ == 'VERB':
                root_verb = tok.head.text
                root_verb_stem = stemmer.stem(root_verb)

                if root_verb_stem in subj_verb:
                    has_subj = False
                    for i in range(tok.i - 1, tok.head.i - 1, -1):
                        if doc[i].dep_ in ['nsubj', 'nsubjpass']:
                            has_subj = True
                            break

                    if not has_subj:
                        subj = subj_verb[root_verb_stem][-1][0]
                        verb = tok.text
                        verb_stem = stemmer.stem(verb)
                        if verb_stem in subj_verb:
                            subj_verb[verb_stem].append([subj, False])
                        else:
                            subj_verb[verb_stem] = [[subj, False]]

        # event modifier (advmod)
        elif tok.dep_ == 'advmod' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = stemmer.stem(verb)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([tok.text, False])
            else:
                event_modifiers[verb_stem] = [[tok.text, False]]

        # are auxpass AUX determined said VBN
        # still advmod ADV are determined VBP
        elif tok.dep_ == 'advmod' and tok.head.pos_ == 'AUX':
            verb = tok.head.head.text
            verb_stem = stemmer.stem(verb)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([tok.text, False])
            else:
                event_modifiers[verb_stem] = [[tok.text, False]]


        # event modifier (npadvmod)
        elif tok.dep_ == 'npadvmod' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = stemmer.stem(verb)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([tok.text, False])
            else:
                event_modifiers[verb_stem] = [[tok.text, False]]

        # event modifier (mark)
        elif tok.dep_ == 'mark' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = stemmer.stem(verb)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([tok.text, False])
            else:
                event_modifiers[verb_stem] = [[tok.text, False]]

        # negation (no NOUN)
        elif tok.text == 'no' and tok.dep_ == 'det' and tok.head.pos_ == 'NOUN':
            noun = tok.head.text
            noun = lemmatizer.lemmatize(noun)
            if noun in noun_neg:
                noun_neg[noun].append([True, False])
            else:
                noun_neg[noun] = [[True, False]]

        elif tok.dep_ == 'neg' and 'V' in tok.head.tag_:
            verb = tok.head.text
            verb_stem = stemmer.stem(verb)
            if verb_stem in verb_stem:
                event_neg[verb_stem].append([True, False])
            else:
                event_neg[verb_stem] = [[True, False]]
    return noun_modifiers, obj_counter, subj_verb, verb_obj, noun_neg, event_neg, event_modifiers


if __name__ == '__main__':
    # !python -m spacy download en_core_web_lg
    nlp = spacy.load('en_core_web_lg')

    # stemmer = PorterStemmer()
    stemmer = LancasterStemmer()

    nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()

    # TODO: make sure the age is connected with hyphen (32-year-old) or 32 years old
    # TODO: clock should be pm (am) or p.m (a.m) (if it appears) in the middle of sentence
    summary = """A 32-year-old female victim got knifepointed by 3 men at a best restaurant in haiti at 9:12 a.m. on Monday.<n>The first man had no description. The second man was described as about 22-year old.<n>The third man was described as about 30-year old."""

    # preprocess_summary
    preprocessed_summ = preprocess_summary(summary)
    doc = nlp(preprocessed_summ)

    print(type(doc))

