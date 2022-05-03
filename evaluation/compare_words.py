from itertools import chain
from nltk.corpus import wordnet as wn
import numpy as np
import re
from scipy import spatial

from utils import get_pos, morphy


# TODO: combine synonyms and antonyms to a single function
def are_synonyms(word_1, word_2, pos):
    """
        word_1: source
        word_2: target
        pos: part of speech of both words
    """

    word_1 = morphy(word_1, pos)
    word_2 = morphy(word_2, pos)

    if not word_1 or not word_2:
        return False

    word_1_syns = get_synonyms(word_1, pos)
    return word_2 in word_1_syns


def get_synonyms(word, pos):
    wn_pos = None
    if pos:
        wn_pos = get_pos(pos.lower())
        if type(wn_pos) == str and not wn_pos:
            print('get_antonym')
            print(word)
            print(pos)
            print('unrecognized pos!')
            print()
            exit(-1)

    word = morphy(word, pos)

    if word:
        synonyms = wn.synsets(word, wn_pos)

        lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
        return lemmas
    else:
        return {}


def has_synonym(word, words_list, pos):
    word = morphy(word, pos)

    if word:
        # check if any of word's synonyms is in words_list
        has_syn = False
        synonyms = get_synonyms(word, pos)
        for syn in synonyms:
            for word in words_list:
                syn_morph = morphy(syn, pos)
                word_morph = morphy(word, pos)
                if syn_morph and word_morph and syn_morph == word_morph:
                    has_syn = True
                    break
            if has_syn:
                return has_syn
        return has_syn
    else:
        return False


def get_antonyms(word, pos):
    wn_pos = None
    if pos:
        wn_pos = get_pos(pos.lower())
        if type(wn_pos) == str and not wn_pos:
            print('get_antonym')
            print(word)
            print(pos)
            print('unrecognized pos!')
            print()
            exit(-1)

    word = morphy(word, pos)

    if word:
        synonyms = wn.synsets(word, wn_pos)

        antonyms = set(
            chain.from_iterable([lemma.antonyms() for word in synonyms for lemma in word.lemmas() if lemma.antonyms()]))
        return set([antonym.name() for antonym in antonyms])
    else:
        return {}


def are_antonyms(word_1, word_2, pos):
    """
        word_1: source
        word_2: target
    """

    word_1 = morphy(word_1, pos)
    word_2 = morphy(word_2, pos)

    if not word_1 or not word_2:
        return False

    word_1_ants = get_antonyms(word_1, pos)
    return word_2 in word_1_ants


def has_antonym(word, words_list, pos):
    word = morphy(word, pos)

    if word:
        # check if any of word's antonyms is in words_list
        has_ant = False
        antonyms = get_antonyms(word, pos)
        for ant in antonyms:
            for word in words_list:
                ant_morph = morphy(ant, pos)
                word_morph = morphy(word, pos)
                if ant_morph and word_morph and ant_morph == word_morph:
                    has_ant = True
                    break
            if has_ant:
                return has_ant
        return has_ant
    else:
        return False


def has_similar_sense(word_1, word_2, pos, threshold):
    if pos.lower() in ['num', 'propn', 'pron']:
        return False

    wn_pos = get_pos(pos)

    if type(wn_pos) == str and not wn_pos:
        print('has_similar')
        print(word_1)
        print(word_2)
        print(pos)
        print('unrecognized pos!')
        print()
        exit(-1)

    word_1 = morphy(word_1, pos)
    word_2 = morphy(word_2, pos)

    if not word_1 or not word_2:
        return False

    word_1_synsets = wn.synsets(word_1, wn_pos)
    word_2_synsets = wn.synsets(word_2, wn_pos)

    max_similarity = 0
    for synset_1 in word_1_synsets:
        for synset_2 in word_2_synsets:
            similarity = synset_1.wup_similarity(synset_2)
            # similarity = synset_1.path_similarity(synset_2)
            if similarity and similarity > max_similarity:
                max_similarity = similarity

    # or use get_most_likely_synset() method !
    return max_similarity >= threshold


def load_embeddings_dict():
    embeddings_dict = {}

    with open('../../extractor/glove.6B.100d.txt', 'r') as fr:
        for line in fr:
            tokens = line.split()
            word = tokens[0]
            embed = np.array(tokens[1:], dtype=np.float64)
            embeddings_dict[word] = embed
    return embeddings_dict


def measure_cosine_similarity(word_1, word_2, embeddings_dict, threshold):
    if word_1.lower() not in embeddings_dict or word_2.lower() not in embeddings_dict:
        return False

    word_1_emb = embeddings_dict[word_1.lower()]
    word_2_emb = embeddings_dict[word_2.lower()]

    result = 1 - spatial.distance.cosine(word_1_emb, word_2_emb)
    return result >= threshold


def get_years(word):
    aged_match = re.match(r'(\d+) aged', word)
    years_old_match = re.match(r'(\d+)[\s]years old', word)

    if aged_match:
        return aged_match.groups()[0]
    elif years_old_match:
        return years_old_match.groups()[0]
    return None


def is_similar(word_1, word_2, pos, embeddings_dict, threshold):
    if len(word_1.split()) > 1:
        return False

    if pos and pos.lower() in ['num', 'propn', 'pron']:
        return False

    # skip time literal with pm or am
    if 'p.m.' in word_1 or 'pm' in word_1 or 'p.m' in word_1 or 'a.m.' in word_1 or 'am' in word_1 or 'a.m' in word_1:
        return False

    if 'p.m.' in word_2 or 'pm' in word_2 or 'p.m' in word_2 or 'a.m.' in word_2 or 'am' in word_2 or 'a.m' in word_2:
        return False

    # lowercase part of speech
    if pos:
        pos = pos.lower()

    word_1 = morphy(word_1, pos)
    word_2 = morphy(word_2, pos)

    if not word_1 or not word_2:
        return False

    if are_antonyms(word_1, word_2, pos):
        return False
    else:
        if are_synonyms(word_1, word_2, pos):
            return True
        else:
            if pos in ['noun', 'verb']:
                # check interval
                if not word_1.isalpha() and word_1.isalnum() and word_1.endswith('s'):
                    years = get_years(word_2)
                    if years:
                        word_2 = years
                    if re.match(r'\d0s', word_1) and (type(word_2) == str and word_2.isnumeric() and (
                            int(word_2) < (int(word_1[:-1]) + 10) and int(word_2) >= int(word_1[:-1]))):
                        return True
                    elif re.match(r'\d\d00s', word_1) and (type(word_2) == str and word_2.isnumeric() and (
                            int(word_2) < (int(word_1[:-1]) + 100) and int(word_2) >= int(word_1[:-1]))):
                        return True
                else:
                    if has_similar_sense(word_1, word_2, pos, threshold):
                        print(f'"{word_1}" and "{word_2}" found to have a similar sense with a threshold of {threshold}.')
                        return True
                    else:
                        return False
            else:
                if measure_cosine_similarity(word_1, word_2, embeddings_dict, threshold):
                    print(f'"{word_1}" and "{word_2}" found to have a similar glove embedding with a threshold of {threshold}.')
                    return True
                else:
                    return False


def has_similar(word, words_list, pos, embeddings_dict, threshold):
    if len(word.split()) > 1:
        return False

    if pos.lower() in ['num', 'propn', 'pron']:
        return False

    if 'p.m.' in word or 'pm' in word or 'p.m' in word or 'a.m.' in word or 'am' in word or 'a.m' in word:
        return False

    if not words_list:
        return False

    word = morphy(word, pos)
    if word:
        if has_antonym(word, words_list, pos):
            return False
        else:
            if has_synonym(word, words_list, pos):
                return True
            else:
                if pos.lower() in ['noun', 'verb']:
                    for sec_word in words_list:
                        sec_word = morphy(sec_word, pos)
                        if sec_word:
                            # check time interval (such as 20s)
                            if word.isalnum() and word.endswith('s'):
                                years = get_years(sec_word)
                                if years:
                                    sec_word = years
                                if re.match(r'\d0s', word) and (type(sec_word) == str and sec_word.isnumeric() and (
                                        int(sec_word) < (int(word[:-1]) + 10) and int(sec_word) >= int(word[:-1]))):
                                    return True
                                elif re.match(r'\d\d00s', word) and (
                                        type(sec_word) == str and sec_word.isnumeric() and (
                                        int(sec_word) < (int(word[:-1]) + 100) and int(sec_word) >= int(word[:-1]))):
                                    return True
                            else:
                                if has_similar_sense(word, sec_word, pos, threshold):
                                    print(f'"{word}" and "{sec_word}" found to have a similar sense with a threshold of {threshold}.')
                                    return True
                    return False
                else:
                    for sec_word in words_list:
                        sec_word = morphy(sec_word, pos)
                        if sec_word:
                            if 'p.m.' in sec_word or 'pm' in sec_word or 'p.m' in sec_word or 'a.m.' in sec_word or 'am' in sec_word or 'a.m' in sec_word:
                                continue
                            if len(sec_word.split()) > 1:
                                continue
                            if measure_cosine_similarity(word, sec_word, embeddings_dict, threshold):
                                print(f'"{word}" and "{sec_word}" found to have a similar glove embedding with a threshold of {threshold}.')
                                return True
                    return False
    else:
        return False
