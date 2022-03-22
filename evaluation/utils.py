def __check_btw_ends(idx, compound_indices):
    for compound_idx in compound_indices:
        if idx > compound_idx[0] and idx < compound_idx[1]:
            return True
    return False


def __can_extend_compound(idx, compound_indices):
    for i in range(len(compound_indices)):
        compound_idx = compound_indices[i]
        if idx == compound_idx[1]:
            return i
    return -1


# compounds
def __get_compounds(doc):
    compounds = []
    compound_indices = []
    for token in doc:
        if token.dep_ == 'compound':
            # if current token.i is between previously found start and end indices of a compound, skip
            if not __check_btw_ends(token.i, compound_indices):
                # if current token.i == end index of a previsouly found compound, extend
                idx_to_extend = __can_extend_compound(token.i, compound_indices)
                if idx_to_extend != -1:
                    compound_indices[idx_to_extend][1] = token.head.i
                else:
                    compound_indices.append([token.i, token.head.i])

    compounds = [doc[compound_idx[0]: compound_idx[1] + 1] for compound_idx in compound_indices]

    return compounds, compound_indices


# combine npadvmod (salmon-colored)
def __combine_npadvmod(doc):
    npadvmod_indices = []
    for token in doc:
        if token.dep_ == 'npadvmod' and token.pos_ == 'NOUN' and token.head.dep_ == 'amod' and token.head.pos_ == 'VERB':
            npadvmod_indices.append([token.i, token.head.i])
    return npadvmod_indices


def __combine_verb_prt(doc):
    verb_indices = []
    for token in doc:
        if token.dep_ == 'prt':
            verb_indices.append([token.head.i, token.i])
    return verb_indices


def __combine_age(doc):
    age_indices = []
    for token in doc:
        if token.dep_ == 'nummod' and 'year' in token.head.text and token.head.dep_ == 'npadvmod':
            age_indices.append([token.i, token.head.head.i])
    return age_indices


# combine time (#p.m./ pm/ a.m. / am)
def __combine_times(doc):
    time_indices = []
    for token in doc:
        # 9:12 9:12 nummod a.m.

        if token.dep_ == 'advmod' and token.text in ['a.m', 'am', 'p.m', 'pm', 'a.m.',
                                                     'p.m.'] and token.head.pos_ == 'NUM':
            time_indices.append([token.head.i, token.i])
        elif token.dep_ == 'nummod' and token.head.text in ['a.m', 'am', 'p.m', 'pm', 'a.m.', 'p.m.']:
            time_indices.append([token.i, token.head.i])
    return time_indices


# combine noun compounds to a single token
def update_tokenizer(doc):
    compounds, compounds_indices = __get_compounds(doc)
    assert len(compounds) == len(compounds_indices)

    age_indices = __combine_age(doc)
    time_indices = __combine_times(doc)
    verb_indices = __combine_verb_prt(doc)
    npadvmod_indices = __combine_npadvmod(doc)

    with doc.retokenize() as retokenizer:
        for i in range(len(compounds)):
            compound = compounds[i]
            retokenizer.merge(doc[compounds_indices[i][0]: compounds_indices[i][1] + 1],
                              attrs={"LEMMA": compound.text.lower()})

        for i in range(len(age_indices)):
            age = doc[age_indices[i][0]: age_indices[i][1] + 1]
            retokenizer.merge(age, attrs={"LEMMA": age.text.lower()})

        for i in range(len(time_indices)):
            time = doc[time_indices[i][0]: time_indices[i][1] + 1]
            retokenizer.merge(time, attrs={"LEMMA": time.text.lower()})

        for i in range(len(verb_indices)):
            verb = doc[verb_indices[i][0]: verb_indices[i][1] + 1]
            retokenizer.merge(verb, attrs={"LEMMA": verb.text.lower()})

        for i in range(len(npadvmod_indices)):
            npadvmod = doc[npadvmod_indices[i][0]: npadvmod_indices[i][1] + 1]
            retokenizer.merge(npadvmod, attrs={"LEMMA": npadvmod.text.lower()})
    return doc

