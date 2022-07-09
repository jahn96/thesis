"""
Data mining to generate real sentences
1. Extract noun, verb, and object and generate fact. (or, using semantic role labeling)
2. Semantic Role Labeling is quite expensive to mine so, just simple NER instead
3. Generate sentences and run summarizer
"""

import spacy
import neuralcoref  # !pip install neuralcoref
import re
import pickle
import tensorflow as tf
import tensorflow_datasets as tfds


def count_entities(doc, named_entities_dist):
    # count named entities
    for ent in doc.ents:
        label = ent.label_
        ent_text = ent.text

        if label in named_entities_dist:
            if ent_text in named_entities_dist[label]:
                named_entities_dist[label][ent_text] += 1
            else:
                named_entities_dist[label][ent_text] = 1
        else:
            named_entities_dist[label] = {ent_text: 1}


# preprocess text
# 1. remove replace text around with hyphen and spaces to a single space
def preprocess_text(document):
    return re.sub(r"\s-\s.*\s-\s", " ", document)


def mine_noun_mod(token):
    """
    Mine a noun and its modifier

    :param token: current token in a document
    :return: a pair of a noun and its modifier
    """
    dep_tag = token.dep_
    pos_tag = token.pos_
    pair = ()
    if dep_tag == "amod" and pos_tag == "ADJ":
        head = token.head
        head_pos_tag = head.pos_

        if head_pos_tag in ["NOUN", "PROPN"]:
            noun = head.text if head_pos_tag in ["PROPN"] else head.lemma_
            adj = token.text
            pair = (adj, noun)

    elif dep_tag == "npadvmod":
        head = token.head
        head_head = head.head

        if head.dep_ == "amod" and head_head.pos_ in ["NOUN", "PROPN"]:
            modifier = token.text + " " + head.text
            noun = head_head.text if head_head.pos_ in ["PROPN"] else head_head.lemma_
            pair = (modifier, noun)
    return pair


def mine_verb_obj(token):
    if token.dep_ == "dobj":
        head = token.head
        if head.pos_ == "VERB":
            return (head.lemma_, token.lemma_)
    return ()


def mine_subj_verb(token):
    if token.dep_ in ["nsubj", "nsubjpass"]:
        head = token.head
        if head.pos_ == "VERB":
            return (token.lemma_, head.lemma_)
    return ()


def check_btw_ends(idx, compound_indices):
    for compound_idx in compound_indices:
        if idx > compound_idx[0] and idx < compound_idx[1]:
            return True
    return False


def can_extend_compound(idx, compound_indices):
    for i in range(len(compound_indices)):
        compound_idx = compound_indices[i]
        if idx == compound_idx[1]:
            return i
    return -1


# compounds
def get_compounds(doc):
    compounds = []
    compound_indices = []
    for token in doc:
        if token.dep_ == "compound":
            # if current token.i is between previously found start and end indices of a compound, skip
            if not check_btw_ends(token.i, compound_indices):
                # if current token.i == end index of a previsouly found compound, extend
                idx_to_extend = can_extend_compound(token.i, compound_indices)
                if idx_to_extend != -1:
                    compound_indices[idx_to_extend][1] = token.head.i
                else:
                    compound_indices.append([token.i, token.head.i])

    compounds = [
        doc[compound_idx[0] : compound_idx[1] + 1] for compound_idx in compound_indices
    ]

    return compounds, compound_indices


# combine noun compounds to a single token
def update_tokenizer_simple(doc):
    compounds, compounds_indices = get_compounds(doc)
    assert len(compounds) == len(compounds_indices)

    with doc.retokenize() as retokenizer:
        for i in range(len(compounds)):
            compound = compounds[i]
            retokenizer.merge(
                doc[compounds_indices[i][0] : compounds_indices[i][1] + 1],
                attrs={"LEMMA": compound.text.lower()},
            )

    return doc


def mine_data(nlp, neuralcoref, data, srl=None):
    """
    Mine data

    :param nlp: spacy nlp model
    :param neuralcoref: neural coreference resolution model
    :param data: data with a required document key
    :return: occurances of noun and its modifier
    """
    if "neuralcoref" not in nlp.pipe_names:
        neuralcoref.add_to_pipe(nlp)

    noun_mod_occurrences = {}
    verb_obj_occurrences = {}
    subj_verb_occurrences = {}

    named_entities_dist = {}

    i = 0
    for datum in data:
        # document = datum['document']
        document = datum["article"].numpy().decode("utf-8")
        document = preprocess_text(document)

        doc = nlp(document)

        doc = nlp(doc._.coref_resolved)
        doc = update_tokenizer_simple(doc)

        count_entities(doc, named_entities_dist)

        for token in doc:
            noun_mod_pair = mine_noun_mod(token)
            verb_obj_pair = mine_verb_obj(token)
            subj_verb_pair = mine_subj_verb(token)

            if len(noun_mod_pair):
                if noun_mod_pair in noun_mod_occurrences:
                    noun_mod_occurrences[noun_mod_pair] += 1
                else:
                    noun_mod_occurrences[noun_mod_pair] = 1

            if len(verb_obj_pair):
                if verb_obj_pair in verb_obj_occurrences:
                    verb_obj_occurrences[verb_obj_pair] += 1
                else:
                    verb_obj_occurrences[verb_obj_pair] = 1

            if len(subj_verb_pair):
                if subj_verb_pair in subj_verb_occurrences:
                    subj_verb_occurrences[subj_verb_pair] += 1
                else:
                    subj_verb_occurrences[subj_verb_pair] = 1

        i += 1
        if i == 30000:
            break

    return (
        noun_mod_occurrences,
        named_entities_dist,
        verb_obj_occurrences,
        subj_verb_occurrences,
    )


if __name__ == "__main__":
    # need to install spacy of version 2.1.0 - !pip install spacy==2.1.0
    # because neuralcoref doesn't work with higher version

    nlp = spacy.load("en")
    neuralcoref.add_to_pipe(nlp)

    cnn_dm_ds = tfds.load("cnn_dailymail", split="train", shuffle_files=True)
    assert isinstance(cnn_dm_ds, tf.data.Dataset)

    (
        noun_mod_occurrences,
        named_entities_dist,
        verb_obj_occurrences,
        subj_verb_occurrences,
    ) = mine_data(nlp, neuralcoref, cnn_dm_ds)

    with open("./mined_facts/noun_mod_occurrences.pkl", "wb") as fw:
        pickle.dump(noun_mod_occurrences, fw)

    with open("./mined_facts/named_entities_dist.pkl", "wb") as fw:
        pickle.dump(named_entities_dist, fw)

    with open("./mined_facts/verb_obj_occurrences.pkl", "wb") as fw:
        pickle.dump(verb_obj_occurrences, fw)

    with open("./mined_facts/subj_verb_occurrences.pkl", "wb") as fw:
        pickle.dump(subj_verb_occurrences, fw)
