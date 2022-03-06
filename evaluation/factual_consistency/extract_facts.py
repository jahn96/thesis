from allennlp.predictors.predictor import Predictor
import re
import spacy
import neuralcoref
from evaluation.factual_consistency.srl2Tree import Srl2Tree
import nltk
from nltk.tokenize import sent_tokenize
from generator.generate_facts import generate_sentence
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
import ast


# TODO: write formula
# TODO: write a paper

# TODO: difficulty in considering all different representation of facts in a summary :(
# ***** TODO: question: how do we extract facts from the output summary? *****
# TODO: we assume that output summary is as simple as the given source document.
# TODO: find a summarizer that summarizes well
# TODO: add negation
# TODO: how do we check if the root verb means have or is ??

def get_srl():
    srl_model = Predictor.from_path(
        "https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
    return srl_model


def traverse_tree(tree):
    for subtree in tree:
        print(subtree)
        if type(subtree) == nltk.tree.Tree:
            # print(subtree)
            if subtree.label()[0] == 'F':
                print(subtree)
                traverse_tree(subtree)
            else:
                print(subtree.label())
                print(subtree[0])


# def extract_facts(srl_model, sent):
#     output = srl_model.predict(sentence=sent)
#
#     facts = {}
#     for verb in output['verbs']:
#         if 'ARG' in verb['description']:
#             fact = re.findall(r'\[(ARG.+?): (.+?)\]', verb['description'])
#             facts[verb['verb']] = fact
#     return facts
#
#
# def filter_facts(nlp, facts):
#     filtered_facts = {}
#     for verb, args in facts.items():
#         filtered_args = []
#         for arg_name, arg_val in args:
#             if not has_verb(nlp, arg_val):
#                 filtered_args.append((arg_name, arg_val))
#         filtered_facts[verb] = filtered_args
#     return filtered_facts
#
#
# def has_verb(nlp, fact):
#     doc = nlp(fact)
#     for tok in doc:
#         if tok.pos_ == 'VERB':
#             return True
#     return False


def evaluate_facts(nlp, category, facts, words, fact_table, threshold):
    visited_facts = set()
    attrs = list(fact_table[0].keys())
    attrs.remove('obj')

    factual_consistency = True
    for indices in sorted(facts):
        fact = facts[indices]
        visited_facts.add(indices)

        verb = fact['V']
        del fact['V']

        # TODO: lesk is not working for color
        verb_sense = lesk(words[indices[0]: indices[1]], verb, pos='v')

        identified_attr = None
        for attr in attrs:
            if identify_attribute(verb_sense, attr, threshold):
                identified_attr = attr

        print("identified_attribute:", identified_attr)
        if identified_attr:
            arg_keys = list(fact.keys())
            # only filter args
            arg_keys = [arg_key for arg_key in arg_keys if len(re.findall(r'^ARG', arg_key))]

            # based on The Proposition Bank (PropBank)
            giver_indices = None
            thing_given_indices = None
            entity_given_indices = None

            for arg_key in arg_keys:
                arg_name, arg_indices = arg_key.split('@')

                if arg_indices in visited_facts:
                    # get noun from the visited fact
                    subject_indices = get_subj_indices_from_fact(facts[arg_indices])
                    if arg_name == 'ARG0':
                        giver_indices = subject_indices
                    elif arg_name == 'ARG1':
                        thing_given = subject_indices
                    elif arg_name == 'ARG2':
                        entity_given_to = subject_indices
                else:
                    if arg_name == 'ARG0':
                        giver_indices = arg_indices
                    elif arg_name == 'ARG1':
                        thing_given = arg_indices
                    elif arg_name == 'ARG2':
                        entity_given_to = arg_indices

            # who did what to whom
            if giver_indices:
                giver = words[giver_indices[0]: giver_indices[1]]
                doc = nlp(' '.join(giver))
                attr_val = ''

                # what
                if thing_given_indices:
                    thing_given = words[thing_given_indices[0]: thing_given_indices[1]]

                    for tok in doc:
                        if tok.pos_ == 'ADP' and tok.dep_ == 'prep' and tok.head.pos_ == 'NOUN':
                            attr_val = tok.head.text
                            attr_synset = lesk(' '.join(thing_given), attr_val, pos='n')

                            if wn.synsets(identified_attr)[0].wup_similarity(attr_synset) < threshold:
                                factual_consistency = False

                for tok in doc:
                    if tok.dep_ == 'nummod' and tok.head.pos_ == 'NOUN':
                        num = tok.text
                        subj = tok.head.text

                        subj_synset = lesk(' '.join(giver), subj, pos='n')

                        if wn.synsets(category)[0].wup_similarity(subj_synset) < threshold:
                            factual_consistency = False

                        # TODO: update the fact_table code here !
                        if attr_val:
                            if subj == category:
                                correct_num = len([val for val in fact_table[identified_attr] if attr_val == val])
                                factual_consistency = (num == correct_num)
                            else:
                                indices = [i for i in range(len(fact_table['obj'])) if fact_table['obj'][i] == subj]

                                correct_num = len(
                                    [idx for idx in indices if fact_table[identified_attr][idx] == attr_val])
                                factual_consistency = (num == correct_num)

        else:
            fact_keys = list(fact.keys())

            # only filter args
            arg_keys = sorted([fact_key for fact_key in fact_keys if re.match(r'^ARG', fact_key)])

            # based on The Proposition Bank (PropBank)
            giver_indices = None
            thing_given_indices = None
            entity_given_indices = None

            # argument modifiers
            negation = False
            where_arg = False
            how_arg = False

            for arg_key in arg_keys:
                arg_name, arg_indices = arg_key.split('@')

                # argument modifiers
                if 'ARGM-NEG' == arg_name:
                    negation = True
                elif 'ARGM-LOC' == arg_name:
                    where_arg = True
                elif 'ARGM-MNR' == arg_name:
                    how_arg = True

                # arguments
                elif not giver_indices:
                    giver_indices = ast.literal_eval(arg_indices)
                elif not thing_given_indices:
                    thing_given_indices = ast.literal_eval(arg_indices)
                elif not entity_given_indices:
                    entity_given_indices = ast.literal_eval(arg_indices)

            objs = [fact['obj'] for fact in fact_table]

            if giver_indices:
                giver_doc = nlp(' '.join(words[giver_indices[0]: giver_indices[1]]))
                update_tokenizer(giver_doc)

                giver = ' '.join(
                    tok.lemma_ for tok in giver_doc if not tok.is_stop)
                print(giver)
                if giver not in objs:
                    print("object is not factually correct :(")
                    factual_consistency = False
                else:
                    if thing_given_indices:
                        thing_given_doc = nlp(' '.join(words[thing_given_indices[0]: thing_given_indices[1]]))
                        update_tokenizer(thing_given_doc)

                        thing_given = ' '.join(
                            tok.lemma_ for tok in thing_given_doc if
                            not tok.is_stop)

                        print(thing_given)

                        has_attr = False
                        for attr in attrs:
                            for fact in fact_table:
                                if fact['obj'] == giver and fact[attr] == thing_given:
                                    has_attr = True

                            if not has_attr:
                                # parse thing_given
                                # thing_given_doc = nlp(' '.join(words[thing_given_indices[0]: thing_given_indices[1]]))
                                # update_tokenizer(thing_given_doc)
                                noun_chunk = next(thing_given_doc.noun_chunks)

                                print(noun_chunk)

                                out = parse_noun_chunk(noun_chunk)
                                adjective = out['ADJ']
                                noun = out['NOUN']

                                if adjective and noun:
                                    if meaning_difference(adjective):
                                        if attr == 'color':
                                            if wn.synset('color.n.01') in wn.synsets(noun):
                                                colors = set()
                                                for fact in fact_table:
                                                    if fact['obj'] == giver:
                                                        colors.add(fact[attr])
                                                if len(colors) != 1:
                                                    has_attr = True
                                        # TODO: add attribute for location
                                        else:
                                            pass
                                    else:
                                        if attr == 'color':
                                            if wn.synset('color.n.01') in wn.synsets(noun):
                                                colors = set()
                                                for fact in fact_table:
                                                    if fact['obj'] == giver:
                                                        colors.add(fact[attr])
                                                if len(colors) == 1:
                                                    has_attr = True
                                        # TODO: add attribute for location
                                        else:
                                            pass
                                else:
                                    factual_consistency = False

                            # TODO: how do we know if it's different color or same color without hard-coding?

                        if negation and has_attr:
                            print("attribute isn't correct :(")
                            factual_consistency = False

            elif thing_given_indices:
                thing_given = ' '.join(
                            tok.lemma_ for tok in nlp(words[thing_given_indices[0]: thing_given_indices[1]]) if
                            not tok.is_stop)
                print(thing_given)
                if thing_given not in objs:
                    print("object is not factually correct :(")
                    factual_consistency = False
                else:
                    if entity_given_indices:
                        entity_given = ' '.join(
                            tok.lemma_ for tok in nlp(words[entity_given_indices[0]: entity_given_indices[1]]) if
                            not tok.is_stop)
                        print(entity_given)
                        has_attr = False
                        for attr in attrs:
                            for fact in fact_table:
                                if fact['obj'] == thing_given and fact[attr] == entity_given:
                                    has_attr = True
                        if negation and has_attr:
                            print("attribute isn't correct :(")
                            factual_consistency = False
            else:
                factual_consistency = False
            # check argument modifiers

    return factual_consistency


def parse_noun_chunk(noun_chunk):
    out = {}
    root = noun_chunk.root

    out[root.pos_] = root.lemma_
    for tok in noun_chunk:
        if tok != root:
            out[tok.pos_] = tok.lemma_
    return out


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
        if token.dep_ == 'compound':
            # if current token.i is between previously found start and end indices of a compound, skip
            if not check_btw_ends(token.i, compound_indices):
                # if current token.i == end index of a previsouly found compound, extend
                idx_to_extend = can_extend_compound(token.i, compound_indices)
                if idx_to_extend != -1:
                    compound_indices[idx_to_extend][1] = token.head.i
                else:
                    compound_indices.append([token.i, token.head.i])

    compounds = [doc[compound_idx[0]: compound_idx[1] + 1] for compound_idx in compound_indices]

    return compounds, compound_indices


# combine compounds and nouns with a modifier to a single token
def update_tokenizer(doc):
    compounds, compounds_indices = get_compounds(doc)
    assert len(compounds) == len(compounds_indices)

    with doc.retokenize() as retokenizer:
        for i in range(len(compounds)):
            compound = compounds[i]
            retokenizer.merge(doc[compounds_indices[i][0]: compounds_indices[i][1] + 1],
                              attrs={"LEMMA": compound.lemma_.lower()})


def meaning_difference(adj):
    synonyms = set()
    antonyms = set()
    for synset in wn.synsets('different'):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name())
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name())

    return adj in synonyms


def get_subj_indices_from_fact(fact):
    args = []
    for arg_key, arg_val in fact.items():
        match = re.match(r'^ARG\d', arg_key)
        if match:
            args.append(arg_key)

    return sorted(args)[0].split('@')[1]


def identify_attribute(verb_sense, attr, threshold):
    """
    Identify attribute of a fact with the verb in the fact
    :param verb_sense:
    :param attr:
    :param threshold:
    :return:
    """
    attr_sense = None

    if attr == 'location':
        # sense of locate
        attr_sense = wn.synset('situate.v.01')
    elif attr == 'color':
        # sense of color
        attr_sense = wn.synset('color.v.01')

    if attr_sense and verb_sense.wup_similarity(attr_sense) >= threshold:
        return True

    return False


if __name__ == '__main__':
    # threshold for word sense disambiguation to check if an attribute/object is appeared as a verb/nounin a fact in the output summary.
    THRESHOLD = 0.8

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en')

    # Add neural coref to SpaCy's pipe
    neuralcoref.add_to_pipe(nlp)

    summary = "Five cubes which were colored differently were placed on the top floor of this building."
    # summary = "He thinks that three marble balls were placed on a table, but they weren't."
    # summary = "He thinks that three black, two white and one yellow cube weren't placed on the top floor of this building, but they were."
    # summary = "Five balls on the top floor of this building are colored red."
    # summary = "The queen has tweeted her thanks to people who sent her 90th birthday messages on social media"
    # summary = "The World Health Organization (WHO) has confirmed that a new type of coronavirus, known as CO-19, has spread from Saudi Arabia to other parts of the world."
    summary = "The tennis balls are yellow and the ping pong balls are orange. The cue ball isn't green. The tennis balls have different colours for each match."

    # You're done. You can now use NeuralCoref as you usually manipulate a SpaCy document annotations.
    doc = nlp(summary)
    # summary = doc._.coref_resolved
    print(summary)

    sents = sent_tokenize(summary)

    predictor = get_srl()

    fact_trees = []

    srl_to_tree_obj = Srl2Tree()

    num_consistent_fact = 0
    num_facts = 0

    for sent in sents:
        srl_out = predictor.predict(sentence=sent)
        print(srl_out)

        words = srl_out['words']
        # tags = [tok.pos_ for tok in nlp(sent)]

        facts = srl_to_tree_obj.get_facts(srl_out)
        print(facts)
        # exit(0)

        # sents, fact_table = generate_sentence('ball', ['color'], tense='present')
        # print(fact_table)
        # sources = ["The cue ball is green. The tennis balls are yellow. The ping pong ball is orange."]

        # fact_table = {'obj': ['cue ball', 'tennis ball', 'ping pong ball'], 'color': ['green', 'yellow', 'orange']}
        fact_table = [{'obj': 'cue ball', 'color': 'green'}, {'obj': 'tennis ball', 'color': 'yellow'},
                      {'obj': 'ping pong ball', 'color': 'orange'}]

        category = 'ball'
        factual_consistency = evaluate_facts(nlp, category, facts, words, fact_table, THRESHOLD)
        print(factual_consistency)
        if factual_consistency:
            num_consistent_fact += 1

    print('factual consistency score:', num_consistent_fact / len(sents))
    # 'situate.v.01'
    #     tree = nltk.tree.Tree.fromstring(tree_str)
    #
    #     print(tree)
    #
    #     fact_trees.append(tree)

    # traverse_tree(fact_trees[0])
    # summary_tree = srl2Tree.Srl2Tree().one_summary(outputs)

    # print(summary_tree)
    # start_time = time.time()
    # print("--- %s seconds ---" % (time.time() - start_time))

# {'verbs': [{'verb': 'Did', 'description': '[V: Did] Uriah honestly think he could beat the game in under three hours ? .', 'tags': ['B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'think', 'description': 'Did [ARG0: Uriah] [ARGM-ADV: honestly] [V: think] [ARG1: he could beat the game in under three hours] ? .', 'tags': ['O', 'B-ARG0', 'B-ARGM-ADV', 'B-V', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1', 'O', 'O']}, {'verb': 'could', 'description': 'Did Uriah honestly think he [V: could] beat the game in under three hours ? .', 'tags': ['O', 'O', 'O', 'O', 'O', 'B-V', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']}, {'verb': 'beat', 'description': 'Did Uriah honestly think [ARG0: he] [ARGM-MOD: could] [V: beat] [ARG1: the game] [ARGM-TMP: in under three hours] ? .', 'tags': ['O', 'O', 'O', 'O', 'B-ARG0', 'B-ARGM-MOD', 'B-V', 'B-ARG1', 'I-ARG1', 'B-ARGM-TMP', 'I-ARGM-TMP', 'I-ARGM-TMP', 'I-ARGM-TMP', 'O', 'O']}], 'words': ['Did', 'Uriah', 'honestly', 'think', 'he', 'could', 'beat', 'the', 'game', 'in', 'under', 'three', 'hours', '?', '.']}
