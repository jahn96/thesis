import spacy
import re
import nltk
from nltk.corpus import wordnet as wn

from extractor.update_tokenizer import update_tokenizer
from utils import morphy, be_verbs, months, list_of_places, prepositions, wh_words


def preprocess_summary(summary: str):
    # ignore phrases
    ignore_phrases = ["the US state of "]
    for ignore_phrase in ignore_phrases:
        summary = summary.replace(ignore_phrase, '')

    # remove special characters
    summary = summary.replace('<n>', ' ')

    # remove everything inside quote not to parse it
    summary = re.sub(r'".*"', '', summary)
    return summary.strip()


def extract_facts_from_summary(summary, nlp):
    noun_modifiers = {}  # (word: [(word, pos), is_found])
    obj_counter = {}
    subj_verb = {}

    # for phrase mod (verb, obj)
    verb_obj = {}

    noun_neg = {}
    event_neg = {}
    subj_verb_obj = {}
    event_modifiers = {}  # also has subordinate clause as its attribute

    count_num_map = {
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four'
    }

    preprocessed_summ = preprocess_summary(summary.strip())
    doc = nlp(preprocessed_summ)
    doc = update_tokenizer(doc)

    for tok in doc:
        # adjective/noun modifier
        if (tok.dep_ == 'amod' or tok.dep_ == 'nmod' or tok.dep_ == 'compound') and tok.head.pos_ in ['NOUN', 'PROPN']:
            # modifier and object
            noun = tok.head.text
            noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
            modifier = tok.text
            if noun in noun_modifiers:
                noun_modifiers[noun].append([[modifier, tok.pos_], False])
            else:
                noun_modifiers[noun] = [[[modifier, tok.pos_], False]]

        # adjective complement
        if tok.dep_ == 'acomp':
            adjective = tok.text
            verb = morphy(tok.head.text, tok.head.pos_) + '_' + str(tok.head.i)
            subj = subj_verb[verb][-1][0][0]

            if subj in noun_modifiers:
                noun_modifiers[subj].append([[adjective, tok.pos_], False])
            else:
                noun_modifiers[subj] = [[[adjective, tok.pos_], False]]

        # appos modifier
        if tok.dep_ == 'appos':  # and tok.pos_ == 'NUM':
            noun = tok.head.text
            noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
            modifier = tok.text
            if noun in noun_modifiers:
                noun_modifiers[noun].append([[modifier, tok.pos_], False])
            else:
                noun_modifiers[noun] = [[[modifier, tok.pos_], False]]

        # clausal modifier of noun
        elif tok.dep_ == 'acl' and tok.pos_ == 'VERB':
            noun = tok.head.text
            noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
            modifier = tok.text
            verb = morphy(modifier, tok.pos_) + '_' + str(tok.i)
            if verb in subj_verb:
                subj_verb[verb].append([[noun, tok.head.pos_], False])
            else:
                subj_verb[verb] = [[[noun, tok.head.pos_], False]]

        # # possessive modifier of noun
        # elif tok.dep_ == 'poss' and tok.head.pos_ in ['NOUN', 'PROPN']:
        #   noun = morphy(tok.head.text, tok.head.pos_)
        #   possessive = tok.text

        #   if noun in noun_modifiers:
        #     noun_modifiers[noun].append([[possessive, tok.pos_],False])
        #   else:
        #     noun_modifiers[noun] = [[[possessive, tok.pos_],False]]

        # miscellanious modifier of noun
        elif tok.dep_ == 'attr' and tok.head.text in be_verbs:
            modifier = tok.text
            verb = morphy(tok.head.text, tok.head.pos_) + '_' + str(tok.head.i)

            if verb in subj_verb:
                subj = subj_verb[verb][-1][0][0]

                if subj in noun_modifiers:
                    noun_modifiers[subj].append([[modifier, tok.pos_], False])
                else:
                    noun_modifiers[subj] = [[[modifier, tok.pos_], False]]

        # noun modifier with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ in ['NOUN', 'PROPN'] and tok.head.dep_ == 'pobj':
            conj = ''

            for i in range(tok.i - 1, -1, -1):
                if doc[i].pos_ == 'CCONJ':
                    conj = doc[i].text
                    break
            if tok.head.head.dep_ == 'prep':
                if tok.head.head.head.pos_ == 'NOUN':
                    noun = tok.head.head.head.text
                    noun = morphy(noun, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)
                    prep = tok.head.head.text
                    head_modifier = prep + ' ' + tok.head.text

                    # modifier = tok.head.head.text + ' ' + tok.text
                    if noun in noun_modifiers:
                        idx = noun_modifiers[noun].index([[head_modifier, tok.head.pos_], False])

                        noun_modifiers[noun][idx][0][0] += (' ' + conj + ' ' + morphy(tok.text, tok.pos_))
                        noun_modifiers[noun][idx][0][1] += (' ' + tok.pos_)
                    else:
                        print('Warning: check conjunction!')
                elif tok.head.head.head.pos_ == 'VERB':
                    verb = tok.head.head.head.text
                    verb_stem = morphy(verb, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)
                    prep = tok.head.head.text
                    head_modifier = prep + ' ' + tok.head.text

                    # modifier = tok.head.head.text + ' ' + tok.text
                    if verb_stem in event_modifiers:
                        idx = event_modifiers[verb_stem].index([[head_modifier, tok.head.pos_], False])
                        # conj = ''

                        # for i in range(tok.i - 1, -1, -1):
                        #   if doc[i].pos_ == 'CCONJ':
                        #     conj = doc[i].text
                        #     break

                        event_modifiers[verb_stem][idx][0][0] += (' ' + conj + ' ' + tok.text)
                        event_modifiers[verb_stem][idx][0][1] += (' ' + tok.pos_)
                    else:
                        print('Warning: check conjunction!')
            elif tok.head.head.dep_ == 'agent':
                verb = tok.head.head.head.text
                verb_stem = morphy(verb, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)
                head_noun = tok.head.text + '_' + str(tok.head.i)

                # modifier = tok.head.head.text + ' ' + tok.text
                # if verb_stem in verb_obj:

                if verb_stem in subj_verb_obj:
                    subj_obj_pairs = subj_verb_obj[verb_stem]

                    for i in range(len(subj_obj_pairs) - 1, -1, -1):
                        subj_obj_pair = subj_obj_pairs[i]
                        subj, obj = subj_obj_pair[0]
                        # subjs, objs = subj_obj_pairs
                        if [head_noun, tok.head.pos_] == obj:
                            obj[0] += (' ' + conj + ' ' + morphy((tok.text + '_' + str(tok.i)), tok.pos_))
                            obj[1] += (' ' + tok.pos_)
                            break

                # in case it's a phrase_mod (verb, obj)
                elif verb_stem in verb_obj:
                    objs = verb_obj[verb_stem]

                    for i in range(len(objs)):
                        obj = objs[i][0]
                        if [head_noun, tok.head.pos_] == obj:
                            obj[0] += (' ' + conj + ' ' + morphy((tok.text + '_' + str(tok.i)), tok.pos_))
                            obj[1] += (' ' + tok.pos_)
                            break
                            # else:
                    #   idx = verb_obj[verb_stem].index([[head_noun, tok.head.pos_], False])

                    #   verb_obj[verb_stem][idx][0][0] += (' ' + conj + ' ' + morphy(tok.text, tok.pos_))
                    #   verb_obj[verb_stem][idx][0][1] += (' ' + tok.pos_)
                else:
                    print('Warning: check conjunction!')

        # noun with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ == 'NOUN':
            conj = ''

            for i in range(tok.i - 1, -1, -1):
                if doc[i].pos_ == 'CCONJ':
                    conj = doc[i].text
                    break

            head_noun = tok.head.text
            head_noun = morphy(head_noun, tok.head.pos_) + '_' + str(tok.head.i)

            noun = tok.text
            noun = morphy(noun, tok.pos_) + '_' + str(tok.i)

            # noun object
            if tok.head.dep_ == 'dobj':
                head_verb = tok.head.head.text
                head_verb_stem = morphy(head_verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                if head_verb_stem in subj_verb_obj:
                    subj_obj_pairs = subj_verb_obj[head_verb_stem]

                    for i in range(len(subj_obj_pairs) - 1, -1, -1):
                        subj_obj_pair = subj_obj_pairs[i]
                        # subj_obj_pair: [[subj, obj], is_found] & subj, obj = [noun, pos]
                        subj, obj = subj_obj_pair[0]
                        # subjs, objs = subj_obj_pairs
                        if [head_noun, tok.head.pos_] == obj:
                            obj[0] += (' ' + conj + ' ' + noun)
                            obj[1] += (' ' + tok.pos_)
                            break

                # in case it's a phrase_mod (verb, obj)
                elif head_verb_stem in verb_obj:
                    objs = verb_obj[head_verb_stem]

                    for i in range(len(objs) - 1, -1, -1):
                        obj = objs[i][0]

                        if [head_noun, tok.head.pos_] == obj:
                            obj[0] += (' ' + conj + ' ' + noun)
                            obj[1] += (' ' + tok.pos_)
                            break

            # noun subject
            if tok.head.dep_ == 'nsubj':
                head_verb = tok.head.head.text
                head_verb_stem = morphy(head_verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                if head_verb_stem in subj_verb:
                    idx = subj_verb[head_verb_stem].index([[head_noun, tok.head.pos_], False])

                    subj_verb[head_verb_stem][idx][0][0] += (' ' + conj + ' ' + noun)
                    subj_verb[head_verb_stem][idx][0][1] += (' ' + tok.pos_)

            # passive noun and subj
            elif tok.head.dep_ == 'nsubjpass':
                head_verb = tok.head.head.text
                head_verb_stem = morphy(head_verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                if head_verb_stem in subj_verb:
                    idx = subj_verb[head_verb_stem].index([[head_noun + '_passive', tok.head.pos_], False])

                    subj_verb[head_verb_stem][idx][0][0] += (' ' + conj + ' ' + noun + '_passive')
                    subj_verb[head_verb_stem][idx][0][1] += (' ' + tok.pos_)

            # noun
            if head_noun in noun_modifiers:
                noun_modifiers[noun] = noun_modifiers[head_noun]

        # verb with conjunction
        elif tok.dep_ == 'conj' and tok.pos_ == 'VERB':
            head_verb = tok.head.text
            verb = tok.text

            head_verb_stem = morphy(head_verb, tok.head.pos_) + '_' + str(tok.head.i)
            verb_stem = morphy(verb, tok.pos_) + '_' + str(tok.i)

            if head_verb_stem in subj_verb:
                subj_verb[verb_stem] = subj_verb[head_verb_stem].copy()

            if head_verb_stem in event_modifiers:
                event_modifiers[verb_stem] = event_modifiers[head_verb_stem].copy()

            if head_verb_stem in event_neg:
                event_neg[verb_stem] = event_neg[head_verb_stem].copy()

        # relative clause (recl)
        elif tok.dep_ == 'relcl':
            if tok.pos_ == 'VERB':
                verb = tok.text
                verb_stem = morphy(verb, tok.pos_) + '_' + str(tok.i)
                noun = tok.head.text
                noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
                if verb_stem in subj_verb:
                    subj_verb[verb_stem].append([[noun, tok.head.pos_], False])
                else:
                    subj_verb[verb_stem] = [[[noun, tok.head.pos_], False]]

                # check another noun connected with conjunction
                nouns = []
                for i in range(tok.head.i + 1, tok.i):
                    curr_tok = doc[i]
                    if curr_tok.dep_ == 'conj' and curr_tok.pos_ == 'NOUN' and curr_tok.head.text == noun:
                        nouns.append(
                            [[morphy(curr_tok.text, curr_tok.pos_) + '_' + str(curr_tok.i), curr_tok.pos_], False])

                for noun in nouns:
                    if verb_stem in subj_verb:
                        subj_verb[verb_stem].append(noun)
                    else:
                        subj_verb[verb_stem] = [noun]

        # verb + 'as' modifier
        elif (tok.dep_ == 'amod' or tok.dep_ == 'pcomp') and tok.head.text == 'as':
            obj = tok.head.head
            modifier = tok.text
            if obj.pos_ == 'VERB':
                # verb = obj.text
                # verb_stem = stemmer.stem(verb)
                # preposition = tok.head.text

                # if verb_stem in event_modifiers:
                #   event_modifiers[verb_stem].append([preposition + ' ' + modifier, False])
                # else:
                #   event_modifiers[verb_stem] = [[preposition + ' ' + modifier, False]]
                verb = obj.text
                verb_stem = morphy(verb, obj.pos_) + '_' + str(obj.i)
                subj = subj_verb[verb_stem][-1][0][0]

                if subj in noun_modifiers:
                    noun_modifiers[subj].append([[modifier, tok.pos_], False])
                else:
                    noun_modifiers[subj] = [[[modifier, tok.pos_], False]]
            elif obj.pos_ == 'NOUN':
                noun = obj.text
                noun = morphy(noun, obj.pos_) + '_' + str(obj.i)
                if noun in noun_modifiers:
                    noun_modifiers[noun].append([[modifier, tok.pos_], False])
                else:
                    noun_modifiers[noun] = [[[modifier, tok.pos_], False]]

        # number modifier
        elif tok.dep_ == 'nummod':
            # year
            if tok.head.text in months:
                year = tok.text
                noun = morphy(tok.head.head.text, tok.head.head.pos_) + '_' + str(tok.head.head.i)
                noun_modifiers[noun].append([[year, tok.pos_], False])

            # count
            elif tok.head.pos_ == 'NOUN':
                noun = tok.head.text
                noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
                if noun in obj_counter:
                    num = count_num_map[tok.text] if tok.text.isnumeric() and int(tok.text) <= 4 else tok.text.lower()
                    obj_counter[noun].append([[num, tok.pos_], False])
                else:
                    num = count_num_map[tok.text] if tok.text.isnumeric() and int(tok.text) <= 4 else tok.text.lower()
                    obj_counter[noun] = [[[num, tok.pos_], False]]

        # subj, verb, obj
        elif tok.dep_ in ['nsubjpass', 'nsubj']:
            # filter out relative clause verb
            if tok.head.dep_ != 'relcl':
                verb = tok.head.text

                verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)

                # ignore be verb
                # if verb_stem == 'be':
                #   continue

                # if verb_stem not in be_verb_stems:
                # add passive verb
                # TODO: check this comment!
                subj = tok.text

                # in case of "most of noun"
                if subj == 'most' and doc[tok.i + 1].dep_ == 'prep':
                    i = 2
                    while doc[tok.i + i].dep_ != 'pobj':
                        i += 1
                    subj = morphy(doc[tok.i + i].text, doc[tok.i + i].pos_) + '_' + str(tok.i + i) + ('' if tok.dep_ == 'nsubj' else '_passive')
                    subj_pos = doc[tok.i + i].pos_
                else:
                    subj = morphy(subj, tok.pos_) + '_' + str(tok.i) + ('' if tok.dep_ == 'nsubj' else '_passive')
                    subj_pos = tok.pos_

                if verb_stem in subj_verb:
                    subj_verb[verb_stem].append([[subj, subj_pos], False])
                else:
                    subj_verb[verb_stem] = [[[subj, subj_pos], False]]

        # active obj
        elif tok.dep_ == 'dobj':
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)
            obj = tok.text
            obj = morphy(obj, tok.pos_) + '_' + str(tok.i)

            if verb_stem in subj_verb:
                if verb_stem in subj_verb_obj:
                    # [[[subj, subj_pos], [obj, obj_pos]], is_found]
                    subj_verb_obj[verb_stem].append([[subj_verb[verb_stem][-1].copy()[0], [obj, tok.pos_]], False])
                else:
                    subj_verb_obj[verb_stem] = [[[subj_verb[verb_stem][-1].copy()[0], [obj, tok.pos_]], False]]

                # remove subject from subj_verb
                subj_verb[verb_stem].remove(subj_verb[verb_stem][-1])

                if not len(subj_verb[verb_stem]):
                    del subj_verb[verb_stem]

            else:
                if verb_stem in verb_obj:
                    verb_obj[verb_stem].append([[obj, tok.pos_], False])
                else:
                    verb_obj[verb_stem] = [[[obj, tok.pos_], False]]

            if tok.head.dep_ == 'conj':
                other_verb = tok.head.head.text
                other_verb_stem = morphy(other_verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                if other_verb_stem in subj_verb:
                    if other_verb_stem in subj_verb_obj:
                        # [[[subj, subj_pos], [obj, obj_pos]], is_found]
                        subj_verb_obj[other_verb_stem].append(
                            [[subj_verb[other_verb_stem][-1].copy()[0], [obj, tok.pos_]], False])
                    else:
                        subj_verb_obj[other_verb_stem] = [
                            [[subj_verb[other_verb_stem][-1].copy()[0], [obj, tok.pos_]], False]]

                    # remove subject from subj_verb
                    subj_verb[other_verb_stem].remove(subj_verb[other_verb_stem][-1])

                    if not len(subj_verb[other_verb_stem]):
                        del subj_verb[other_verb_stem]

                elif other_verb_stem in subj_verb_obj:
                    if verb_stem in subj_verb_obj:
                        subj_verb_obj[verb_stem].append(subj_verb_obj[other_verb_stem][-1].copy())
                    else:
                        subj_verb_obj[verb_stem] = [subj_verb_obj[other_verb_stem][-1].copy()]

                    verb_obj[verb_stem].remove(verb_obj[verb_stem][-1])

                    if not len(verb_obj[verb_stem]):
                        del verb_obj[verb_stem]

                else:
                    # if other_verb_stem doesn't have obj
                    # killed advcl VERB apprehended apprehended VBN
                    # one nummod NUM person killed NN
                    # person dobj NOUN killed apprehended VBD
                    # and cc CCONJ killed apprehended VBD
                    # wounded conj VERB killed apprehended VBD
                    # several amod ADJ people wounded NNS
                    # people dobj NOUN wounded killed VBD
                    # . punct PUNCT apprehended apprehended VBN

                    has_dobj = False
                    for i in range(tok.i - 1, tok.head.head.i, -1):
                        if doc[i].dep_ == 'dobj':
                            has_dobj = True
                            break

                    if not has_dobj:
                        if other_verb_stem in verb_obj:
                            verb_obj[other_verb_stem].append([[obj, tok.pos_], False])
                        else:
                            verb_obj[other_verb_stem] = [[[obj, tok.pos_], False]]


        # prepositional complement (preposition + adverbial clause)
        elif tok.dep_ == 'pcomp' and tok.pos_ == 'VERB':
            verb = morphy(tok.text, tok.pos_) + '_' + str(tok.i)
            if verb in subj_verb:
                print(subj_verb)
                print(verb)
                subj = subj_verb[verb][-1][0]
                prep = tok.head.text
                connective = doc[tok.head.i + 1].text
                phrase_mod = prep + ' ' + connective + ' ' + subj[0] + ' ' + verb

                # noun phrase modifier
                if tok.head.head.pos_ == 'NOUN':
                    noun = morphy(tok.head.head.text, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                    if noun in noun_modifiers:
                        noun_modifiers[noun].append([[phrase_mod, subj[1] + ' ' + tok.pos_], False])
                    else:
                        noun_modifiers[noun] = [[[phrase_mod, subj[1] + ' ' + tok.pos_], False]]

                elif tok.head.head.head.pos_ == 'NOUN':
                    noun = morphy(tok.head.head.head.text, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)

                    if noun in noun_modifiers:
                        noun_modifiers[noun].append([[phrase_mod, subj[1] + ' ' + tok.pos_], False])
                    else:
                        noun_modifiers[noun] = [[[phrase_mod, subj[1] + ' ' + tok.pos_], False]]

        # preposition object (phrase modifier)
        elif tok.dep_ == 'pobj':
            # passive obj
            preposition = tok.head

            if preposition.dep_ == 'agent':
                verb = tok.head.head.text
                verb_stem = morphy(verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)
                obj = tok.text
                obj = morphy(obj, tok.pos_) + '_' + str(tok.i)

                if verb_stem in subj_verb:
                    if verb_stem in subj_verb_obj:
                        # [[[subj, subj_pos], [obj, obj_pos]], is_found]
                        subj_verb_obj[verb_stem].append([[subj_verb[verb_stem][-1].copy()[0], [obj, tok.pos_]], False])
                    else:
                        subj_verb_obj[verb_stem] = [[[subj_verb[verb_stem][-1].copy()[0], [obj, tok.pos_]], False]]

                    # remove subject from subj_verb
                    subj_verb[verb_stem].remove(subj_verb[verb_stem][-1])
                    if not len(subj_verb[verb_stem]):
                        del subj_verb[verb_stem]
                else:
                    if verb_stem in verb_obj:
                        verb_obj[verb_stem].append([[obj, tok.pos_], False])
                    else:
                        verb_obj[verb_stem] = [[[obj, tok.pos_], False]]

                if tok.head.dep_ == 'conj':
                    other_verb = tok.head.head.text
                    other_verb_stem = morphy(tok.head.head.text, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                    if other_verb_stem in subj_verb:
                        if other_verb_stem in subj_verb_obj:
                            # [[[subj, subj_pos], [obj, obj_pos]], is_found]
                            subj_verb_obj[other_verb_stem].append(
                                [[subj_verb[other_verb_stem][-1].copy()[0], [obj, tok.pos_]], False])
                        else:
                            subj_verb_obj[other_verb_stem] = [
                                [[subj_verb[other_verb_stem][-1].copy()[0], [obj, tok.pos_]], False]]

                        # remove subject from subj_verb
                        subj_verb[other_verb_stem].remove(subj_verb[other_verb_stem][-1])

                        if not len(subj_verb[other_verb_stem]):
                            del subj_verb[other_verb_stem]
                    else:
                        if other_verb_stem in verb_obj:
                            verb_obj[other_verb_stem].append([[obj, tok.pos_], False])
                        else:
                            verb_obj[other_verb_stem] = [[[obj, tok.pos_], False]]


            # location, place, time, ... modifiers
            else:
                # noun phrase modifier
                if tok.head.head.pos_ == 'NOUN':
                    noun = tok.head.head.text
                    noun = morphy(noun, tok.head.head.pos_) + '_' + str(tok.head.head.i)
                    # phrase_mod = tok.head.text + ' ' + tok.text

                    # if tok.text is a place, then ignore prep
                    if tok.text in list_of_places:
                        phrase_mod = tok.text
                    else:
                        prep = tok.head.text
                        phrase_mod = prep + ' ' + tok.text

                    if noun in noun_modifiers:
                        noun_modifiers[noun].append([[phrase_mod, tok.pos_], False])
                    else:
                        noun_modifiers[noun] = [[[phrase_mod, tok.pos_], False]]
                # verb phrase modifier
                elif tok.head.head.pos_ == 'VERB':
                    # ?? Check possible case for this?
                    if tok.head.head.dep_ == 'prep':
                        preposition = tok.head.head.text + ' ' + preposition.text

                        phrase_mod = preposition + ' ' + tok.text
                        verb = tok.head.head.head.text
                        verb_stem = morphy(verb, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)
                        subj = subj_verb[verb_stem][-1][0][0]

                        if subj in noun_modifiers:
                            noun_modifiers[subj].append([[phrase_mod, tok.pos_], False])
                        else:
                            noun_modifiers[subj] = [[[phrase_mod, tok.pos_], False]]

                    # verbs are conjugated - killed and injured in the shooting
                    elif tok.head.head.dep_ == 'conj':
                        phrase_mod = preposition.text + ' ' + tok.text

                        verb = tok.head.head.text
                        other_verb = tok.head.head.head.text

                        verb_morph = morphy(verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)
                        other_verb_morph = morphy(other_verb, tok.head.head.head.pos_) + '_' + str(tok.head.head.head.i)

                        if verb_morph in event_modifiers:
                            event_modifiers[verb_morph].append([[phrase_mod, tok.pos_], False])
                        else:
                            event_modifiers[verb_morph] = [[[phrase_mod, tok.pos_], False]]

                        if other_verb_morph in event_modifiers:
                            event_modifiers[other_verb_morph].append([[phrase_mod, tok.pos_], False])
                        else:
                            event_modifiers[other_verb_morph] = [[[phrase_mod, tok.pos_], False]]

                    else:
                        verb = tok.head.head.text
                        verb_stem = morphy(verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)

                        if preposition.text.lower() == 'as':
                            # get subj
                            subj = subj_verb[verb_stem][-1][0][0]
                            if subj in noun_modifiers:
                                noun_modifiers[subj].append([[tok.text, tok.pos_], False])
                            else:
                                noun_modifiers[subj] = [[[tok.text, tok.pos_], False]]

                        else:
                            phrase_mod = preposition.text + ' ' + tok.text
                            if verb_stem in event_modifiers:
                                event_modifiers[verb_stem].append([[phrase_mod, tok.pos_], False])
                            else:
                                event_modifiers[verb_stem] = [[[phrase_mod, tok.pos_], False]]

        # adverbial clause modifier (advcl)
        elif tok.dep_ == 'advcl' and tok.pos_ == 'VERB':

            if tok.head.pos_ == 'VERB':
                root_verb = tok.head.text
                root_verb_stem = morphy(root_verb, tok.head.pos_) + '_' + str(tok.head.i)

                # TODO: check what this code does
                if root_verb_stem in subj_verb:
                    has_subj = False
                    for i in range(tok.i - 1, tok.head.i - 1, -1):
                        if doc[i].dep_ in ['nsubj', 'nsubjpass']:
                            has_subj = True
                            break

                    if not has_subj:
                        subj = subj_verb[root_verb_stem][-1][0]
                        verb = tok.text
                        verb_stem = morphy(verb, tok.pos_) + '_' + str(tok.i)
                        if verb_stem in subj_verb:
                            subj_verb[verb_stem].append([subj, False])
                        else:
                            subj_verb[verb_stem] = [[subj, False]]

                sub_verb = morphy(tok.text, tok.pos_) + '_' + str(tok.i)

                # subordinate clause (event modifier) # main verb (main subj, connective, sub subj, sub verb)
                has_sub_ord = False
                if root_verb_stem in subj_verb and sub_verb in subj_verb:
                    main_subj = subj_verb[root_verb_stem][-1][0]
                    sub_subj = subj_verb[sub_verb][-1][0]
                    has_sub_ord = True
                elif root_verb_stem in subj_verb_obj and sub_verb in subj_verb_obj:
                    main_subj = subj_verb_obj[root_verb_stem][-1][0][0]
                    sub_subj = subj_verb_obj[sub_verb][-1][0]
                    has_sub_ord = True

                # adverbial clause with connective
                if has_sub_ord and sub_verb in event_modifiers:
                    connective = event_modifiers[sub_verb][-1][0]

                    if connective[0] in prepositions:

                        # remove connective from event modifier
                        event_modifiers[sub_verb].remove([connective, False])

                        if not len(event_modifiers[sub_verb]):
                            del event_modifiers[sub_verb]

                        if root_verb_stem in event_modifiers:
                            event_modifiers[root_verb_stem].append([[(main_subj[0], connective[0], sub_subj[0],
                                                                      sub_verb), (
                                                                     main_subj[1], connective[1], sub_subj[1],
                                                                     tok.pos_)], False])
                            pass
                        else:
                            event_modifiers[root_verb_stem] = [[[(main_subj[0], connective[0], sub_subj[0], sub_verb),
                                                                 (main_subj[1], connective[1], sub_subj[1], tok.pos_)],
                                                                False]]

        # event modifier (advmod)
        elif tok.dep_ == 'advmod' and tok.head.pos_ == 'VERB' and tok.text.lower() not in wh_words:
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([[tok.text, tok.pos_], False])
            else:
                event_modifiers[verb_stem] = [[[tok.text, tok.pos_], False]]

        elif tok.dep_ == 'oprd' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)

            if verb_stem in subj_verb_obj:
                obj = subj_verb_obj[verb_stem][-1][0][1][0]
                if obj in noun_modifiers:
                    noun_modifiers[obj].append([[tok.text, tok.pos_], False])
                else:
                    noun_modifiers[obj] = [[[tok.text, tok.pos_], False]]

            elif verb_stem in verb_obj:
                obj = verb_obj[verb_stem][-1][0][0]
                if obj in noun_modifiers:
                    noun_modifiers[obj].append([[tok.text, tok.pos_], False])
                else:
                    noun_modifiers[obj] = [[[tok.text, tok.pos_], False]]

            # if verb_stem in event_modifiers:
            #   event_modifiers[verb_stem].append([[tok.text, tok.pos_], False])
            # else:
            #   event_modifiers[verb_stem] = [[[tok.text, tok.pos_], False]]

        # are auxpass AUX determined said VBN
        # still advmod ADV are determined VBP
        elif tok.dep_ == 'advmod' and tok.head.pos_ == 'AUX':
            verb = tok.head.head.text
            verb_stem = morphy(verb, tok.head.head.pos_) + '_' + str(tok.head.head.i)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([[tok.text, tok.pos_], False])
            else:
                event_modifiers[verb_stem] = [[[tok.text, tok.pos_], False]]

        # event modifier (npadvmod)
        elif tok.dep_ == 'npadvmod' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([[tok.text, tok.pos_], False])
            else:
                event_modifiers[verb_stem] = [[[tok.text, tok.pos_], False]]

        # event modifier (mark)
        elif tok.dep_ == 'mark' and tok.head.pos_ == 'VERB':
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)
            if verb_stem in event_modifiers:
                event_modifiers[verb_stem].append([[tok.text, tok.pos_], False])
            else:
                event_modifiers[verb_stem] = [[[tok.text, tok.pos_], False]]

        # event modifier (xcomp)
        elif tok.dep_ == 'xcomp' and tok.pos_ == 'VERB' and tok.head.pos_ == 'VERB':
            i = 1
            while doc[tok.i - i].dep_ != 'aux':
                i += 1
            preposition = doc[tok.i - i].text
            main_verb = morphy(tok.head.text, tok.head.pos_) + '_' + str(tok.head.i)
            inf_verb = morphy(tok.text, tok.pos_)
            phrase_mod = preposition + ' ' + inf_verb

            if main_verb in event_modifiers:
                event_modifiers[main_verb].append([[phrase_mod, tok.pos_], False])
            else:
                event_modifiers[main_verb] = [[[phrase_mod, tok.pos_], False]]

        # negation (no NOUN)
        elif tok.text == 'no' and tok.dep_ == 'det' and tok.head.pos_ == 'NOUN':
            noun = tok.head.text
            noun = morphy(noun, tok.head.pos_) + '_' + str(tok.head.i)
            if noun in noun_neg:
                noun_neg[noun].append([[True, tok.pos_], False])
            else:
                noun_neg[noun] = [[[True, tok.pos_], False]]

        elif tok.dep_ == 'neg' and 'V' in tok.head.tag_:
            verb = tok.head.text
            verb_stem = morphy(verb, tok.head.pos_) + '_' + str(tok.head.i)
            if verb_stem in verb_stem:
                event_neg[verb_stem].append([[True, tok.pos_], False])
            else:
                event_neg[verb_stem] = [[[True, tok.pos_], False]]

    # remove subj be-verb relations
    for be_verb in be_verbs:
        be_verb_morph = morphy(be_verb, 'verb')
        new_subj_verb = subj_verb.copy()
        for verb in subj_verb:
            if be_verb_morph in verb:
                del new_subj_verb[verb]
        subj_verb = new_subj_verb

    return noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg, event_neg, event_modifiers


if __name__ == '__main__':
    # !python -m spacy download en_core_web_lg if it's not installed
    nlp = spacy.load('en_core_web_lg')
    summary = """
    Police are investigating the shooting death of a French soldier in the U.S.
    """
    noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg, event_neg, event_modifiers = extract_facts_from_summary(summary, nlp)


    # A det DET soldier stabbed NN
    # soldier nsubjpass NOUN stabbed stabbed VBN
    # and cc CCONJ soldier stabbed NN
    # his poss PRON girlfriend soldier NN
    # girlfriend conj NOUN soldier stabbed NN
    # were auxpass AUX stabbed stabbed VBN
    # stabbed ROOT VERB stabbed stabbed VBN
    # to prep ADP stabbed stabbed VBN
    # death pobj NOUN to stabbed IN
    # in prep ADP stabbed stabbed VBN
    # a det DET bar in NN
    # bar pobj NOUN in stabbed IN
    # by agent ADP stabbed stabbed VBN
    # two nummod NUM tourists by NNS
    # tourists pobj NOUN by stabbed IN
    # . punct PUNCT stabbed stabbed VBN

    print(noun_modifiers)
    print(obj_counter)
    print(subj_verb)
    print(verb_obj)
    print(subj_verb_obj)
    print(noun_neg)
    print(event_neg)
    print(event_modifiers)
