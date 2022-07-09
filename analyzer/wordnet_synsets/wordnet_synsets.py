import pickle
from nltk.corpus import wordnet as wn


def load_synsets():
    noun_synsets = pickle.load(open("./analyzer/wordnet_synsets/extracted_synsets/noun_syns.pickle", "rb"))
    adj_synsets = pickle.load(open("./analyzer/wordnet_synsets/extracted_synsets/adj_syns.pickle", "rb"))
    verb_synsets = pickle.load(open("./analyzer/wordnet_synsets/extracted_synsets/verb_syns.pickle", "rb"))
    adv_synsets = pickle.load(open("./analyzer/wordnet_synsets/extracted_synsets/adv_syns.pickle", "rb"))

    return noun_synsets, adj_synsets, verb_synsets, adv_synsets


def get_top_n_synsets(synsets, n):
    sorted_synsets = sorted(synsets.items(), key=lambda item: -item[1])[:n]
    return sorted_synsets


def get_wordnet_distance(synset_1, synset_2):
    """
      Based on the shortest path that connects the senses in the is-a (hypernym/hypnoym) taxonomy.
      Distance from synset to lowest common hypernym

      0.5 - right above (1 / (dist + 1)), ...

      return:
          distance from synset_1 to synset_2
    """
    return synset_1.path_similarity(synset_2)


def get_similarity_to_lch(lch, synsets):
    similarities = []
    for synset in synsets:
        similarity = get_wordnet_distance(wn.synset(synset), lch)
        similarities.append(similarity)

    return similarities


def get_most_likely_synset(token, pos, noun_synsets, adj_synsets, adv_synsets, verb_synsets):
    token_synsets = []
    if pos == 'noun':
        for key in noun_synsets:
            if token.lower() in key:
                token_synsets.append({key: noun_synsets[key]})
    elif pos == 'adj':
        for key in adj_synsets:
            if token.lower() in key:
                token_synsets.append({key: adj_synsets[key]})
    elif pos == 'adv':
        for key in adv_synsets:
            if token.lower() in key:
                token_synsets.append({key: adv_synsets[key]})
    elif pos == 'verb':
        for key in verb_synsets:
            if token.lower() in key:
                token_synsets.append({key: verb_synsets[key]})
    if not token_synsets:
        return []

    return list(sorted(token_synsets, key=lambda x: -list(x.values())[0])[0].keys())[0]
