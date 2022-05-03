from itertools import chain, combinations

from evaluation.compare_words import is_similar, has_similar
from extractor.wordnet_synsets.wordnet_synsets import get_most_likely_synset, get_similarity_to_lch
from utils import count_str_int_map, count_text_set, morphy, prepositions
from nltk.corpus import wordnet as wn


def count_total_fact(table):
    total_fact = 0
    for table_el in table:
        for key in table_el:
            for attr in table_el[key]:
                if attr not in ['passive', 'kind']:
                    # skip subj and obj pair but keep verb obj
                    if attr == 'obj' and 'subj' in table_el[key]:
                        continue
                    if type(table_el[key][attr]) == list:
                        total_fact += len(table_el[key][attr])
                    elif type(table_el[key][attr]) == str and ' or ' in table_el[key][attr]:
                        total_fact += len(table_el[key][attr].split(' or '))
                    # add and
                    elif type(table_el[key][attr]) == str and ' and ' in table_el[key][attr]:
                        if table_el[key][attr].split()[0] == 'between':
                            total_fact += 1
                        else:
                            total_fact += len(table_el[key][attr].split(' and '))
                    else:
                        total_fact += 1
    return total_fact


def handle_verb_edge_cases(fact_verb, verb):
    # handling led up vs led
    splitted_fact_verb = fact_verb.lower().split()
    splitted_verb = verb.lower().split()
    if len(splitted_fact_verb) == 2 and len(splitted_verb) == 1:
        return splitted_fact_verb[0]
    else:
        return fact_verb


def split_connected_words_helper(attr, conjunction, prepositions):
    new_attrs = []
    # if it has a preposition and the preposition is a single token
    if attr.split(' ', 1)[0] in prepositions:
        preposition = attr.split(' ', 1)[0]
        words = attr.split(' ', 1)[1].split(conjunction)
        for word in words:
            new_attrs.append(preposition + ' ' + word.strip())

    # if it has a preposition and the preposition is multiple tokens (For example, according to)
    elif len(attr.split(' ')) > 2 and ' '.join(attr.split(' ')[:2]) in prepositions:
        preposition = ' '.join(attr.split(' ', 2)[:2])
        words = attr.split(' ', 2)[2].split(conjunction)
        for word in words:
            new_attrs.append(preposition + ' ' + word.strip())

    # if it doesn't contain a preposition
    else:
        words = attr.split(conjunction)
        for word in words:
            new_attrs.append(word.strip())
    return new_attrs


def split_connected_words(attrs, prepositions):
    new_attrs = []
    for attr in attrs:
        if type(attr) != str:
            continue
        if ' and ' in attr:
            new_attrs.extend(split_connected_words_helper(attr, ' and ', prepositions))
        elif ' or ' in attr:
            new_attrs.extend(split_connected_words_helper(attr, ' or ', prepositions))
        else:
            new_attrs.append(attr)
    return new_attrs


related_attr_vals = set()
visited = []
related_attrs = ['place', 'time', 'location', 'month', 'year']


# place, time, location, month, ...
def get_related_child_attrs(word, pos, threshold, prepositions, table, attrs, visited, embeddings_dict):
    for el in table:

        for fact_type in el:
            fact = el[fact_type]

            fact_kind = fact['kind']

            if fact in visited:
                continue

            if (fact_kind.lower() == word.lower() or is_similar(word, fact_kind, pos, embeddings_dict, threshold)) \
                    or ('subj' in fact and (
                    fact['subj'].lower() == word.lower() or is_similar(word, fact['subj'], pos, embeddings_dict, threshold))):
                visited.append(fact)
                for attr in fact:
                    if attr == 'kind' or attr == 'passive':
                        continue

                    attr_val = fact[attr]
                    if type(attr_val) == list:
                        for val in attr_val:
                            if attr in related_attrs:
                                attrs.add(val)

                            if attr == 'phrase_mod':
                                obj = ''
                                if val.split(' ')[0] in prepositions:
                                    obj = ' '.join(val.split(' ')[1:])
                                elif ' '.join(val.split(' ')[:2]) in prepositions:
                                    obj = ' '.join(val.split(' ')[2:])

                                # to prevent the cycle
                                if obj != word:
                                    get_related_child_attrs(obj, None, threshold, prepositions, table, attrs, visited, embeddings_dict)
                    else:
                        if attr in related_attrs:
                            attrs.add(attr_val)

                        if attr == 'phrase_mod':
                            obj = ''
                            if attr_val.split(' ')[0] in prepositions:
                                obj = ' '.join(attr_val.split(' ')[1:])
                            elif ' '.join(attr_val.split(' ')[:2]) in prepositions:
                                obj = ' '.join(attr_val.split(' ')[2:])

                            # to prevent the cycle
                            if obj != word:
                                get_related_child_attrs(obj, None, threshold, prepositions, table, attrs, visited, embeddings_dict)


def handle_modifiers_helper(mod, attrs, prepositions, embeddings_dict, threshold):
    fact_count = 0
    has_mod = False

    # check if mod is phrase mod
    if mod[0][0].split(' ')[0] in prepositions or ' '.join(mod[0][0].split(' ')[:2]) in prepositions:
        if mod[0][0].split(' ')[0] in prepositions:
            preposition = mod[0][0].split(' ')[0]
            obj = ' '.join(mod[0][0].split(' ')[1:])
            poses = mod[0][1].split()
        else:
            preposition = ' '.join(mod[0][0].split(' ')[: 2])
            obj = ' '.join(mod[0][0].split(' ')[2:])
            poses = mod[0][1].split()

        # drop prepositions of attributes that start with preposition
        phrase_mod_attrs = []
        for attr in attrs:
            if type(attr) != str:
                continue
            if attr.split()[0] == preposition:
                phrase_mod_attrs.append(' '.join(attr.split()[1:]))
            elif ' '.join(attr.split()[: 2]) == preposition:
                phrase_mod_attrs.append(' '.join(attr.split()[2:]))
            # skip attribute that starts with preposition but doesn't match with the preposition of the current word
            elif attr.split()[0] in prepositions:
                continue
            else:
                phrase_mod_attrs.append(attr)

        # in case when it's exactly same
        has_mod = obj in phrase_mod_attrs

        if not has_mod:

            # in case there is multiple pobjs such as between soldier and tourist
            if ' and ' in obj:
                syn_count = 0
                for i in range(len(obj.split(' and '))):
                    pobj = obj.split(' and ')[i]
                    pos = poses[i]

                    if pobj.strip() in attrs or has_similar(pobj.strip(), phrase_mod_attrs, pos, embeddings_dict, threshold):
                        syn_count += 1
                has_mod = (syn_count == len(obj.split('and')))

            elif ' or ' in obj:
                for i in range(len(obj.split(' or '))):
                    pobj = obj.split(' or ')[i]
                    pos = poses[i]

                    if pobj.strip() in attrs or has_similar(pobj.strip(), phrase_mod_attrs, pos, embeddings_dict, threshold):
                        has_mod = True
                        break

            else:
                has_mod = has_similar(obj.strip(), phrase_mod_attrs, ' '.join(poses), embeddings_dict, threshold)

    else:
        # check synonym
        has_mod = mod[0][0] in attrs

        # filter attrs that are made up of multiple tokens without 'and' or 'or
        attrs = [attr for attr in attrs if
                 type(attr) == str and (len(attr.split()) == 1 or ('and' in attr or 'or' in attr))]

        if not has_mod:
            modifier = mod[0][0]
            if ' and ' in modifier:
                poses = mod[0][1].split()
                syn_count = 0
                for i in range(len(modifier.split(' and '))):
                    obj = modifier.split(' and ')[i]
                    pos = poses[i]
                    if obj in attrs or has_similar(obj, attrs, pos, embeddings_dict, threshold):
                        syn_count += 1
                has_mod = (syn_count == len(modifier.split('and')))
            elif ' or ' in modifier:
                poses = mod[0][1].split()
                for i in range(len(modifier.split(' or '))):
                    obj = modifier.split(' or ')[i]
                    pos = poses[i]
                    if obj in attrs or has_similar(obj, attrs, pos, embeddings_dict, threshold):
                        has_mod = True
                        break
            else:
                has_mod = has_similar(modifier, attrs, mod[0][1], embeddings_dict, threshold)

    if not mod[1] and has_mod:
        fact_count += 1
        mod[1] = True
    return fact_count


def filter_attrs(pos, fact, fact_type, include_phrase_mod):
    """
      pos: part of speech of a word
      fact: fact to match
      fact_type: type of fact such as 'event', 'object', or 'person'
      include_phrase_mod: whether to filter phrase mod - True means filter
    """
    # attributes that are nouns!
    noun_attrs = ['place', 'subj', 'obj', 'location', 'time', 'day']

    if pos.lower() in ['noun', 'propn']:
        if include_phrase_mod:
            return set(fact[fact_type][key] for key in fact[fact_type] if
                       key != 'kind' and key != 'passive' and key != 'phrase_mod')
        else:
            return set(fact[fact_type][key] for key in fact[fact_type] if key != 'kind' and key != 'passive')
    else:
        if include_phrase_mod:
            return set(fact[fact_type][key] for key in fact[fact_type] if
                       key != 'kind' and key != 'passive' and key != 'phrase_mod' and key not in noun_attrs)
        else:
            return set(fact[fact_type][key] for key in fact[fact_type] if
                       key != 'kind' and key != 'passive' and key not in noun_attrs)


# pos, fact, fact_type, include_phrase_mod
# def handle_modifiers(attrs, modifiers, prepositions, threshold):
# fact_type: 'object', 'event', ...
# fact: fact element in a table
def handle_modifiers(fact, fact_type, obj, obj_pos, modifiers, prepositions, threshold, table, embeddings_dict, include_phrase_mod=False,
                     only_phrase_mod=False):
    fact_count = 0
    for mod in modifiers:
        # if it's checked before, then skip
        if mod[1]:
            continue

        if only_phrase_mod:
            attrs = fact[fact_type]['phrase_mod']
        else:
            attrs = filter_attrs(mod[0][1], fact, fact_type, include_phrase_mod)
            # go through the fact tree and get all realted attributes of an object
            related_attr_vals = set()
            visited = []
            # get related child attrs of an object
            # TODO: see if we need to filter out attributes here
            get_related_child_attrs(obj, obj_pos, threshold, prepositions, table, related_attr_vals, visited, embeddings_dict)
            attrs = attrs.union(related_attr_vals)

        attrs = split_connected_words(attrs, prepositions)
        fact_count += handle_modifiers_helper(mod, attrs, prepositions, embeddings_dict, threshold)
    return fact_count


def match_obj_helper(obj, fact_obj_list, obj_pos, threshold, victim_map, embeddings_dict):
    for fact_obj in fact_obj_list:
        if (fact_obj.lower() in victim_map and obj.lower() == victim_map[
            fact_obj.lower()]) or obj.lower() == fact_obj.lower() or is_similar(obj.lower(), fact_obj.lower(), obj_pos,
                                                                                embeddings_dict,
                                                                                threshold):
            return True
    return False


def split_obj(obj):
    if 'or' in obj:
        objs = obj.split('or')
    elif 'and' in obj:
        objs = obj.split('and')
    else:
        objs = [obj]

    return objs


# to match either sub or obj
def match_obj(verb, obj, obj_pos, threshold, fact_type, table, victim_map, embeddings_dict):
    for f_type in table:
        if f_type == fact_type:
            fact = table[f_type]
            fact_verb = fact['kind'].lower()
            fact_verb = handle_verb_edge_cases(fact_verb, verb).lower()

            if (fact_verb == verb.lower() or is_similar(fact_verb, verb.lower(), 'verb', embeddings_dict, threshold)):
                if 'subj' in fact:
                    fact_subj = fact['subj'].lower()

                    fact_subjs = split_obj(fact_subj)

                    is_matched = match_obj_helper(obj, fact_subjs, obj_pos, threshold, victim_map, embeddings_dict)
                    if is_matched:
                        return True
                    else:
                        if 'passive' in fact:
                            if 'obj' in fact:
                                fact_subj = fact['obj'].lower()

                                fact_subjs = split_obj(fact_subj)

                                if match_obj_helper(obj, fact_subjs, obj_pos, threshold, victim_map, embeddings_dict):
                                    return True

    return False


def match_anded_obj(obj, fact_obj_list, pos, threshold, victim_map, embeddings_dict):
    objs = obj.split('and')
    poses = pos.split()

    # sanity check
    assert len(objs) == len(poses)

    num_obj_matched = 0
    for i in range(len(objs)):
        obj = objs[i]
        pos = poses[i]
        for fact_obj in fact_obj_list:
            if ((fact_obj.lower() in victim_map and obj.lower() == victim_map[fact_obj.lower()]) or (
                    obj.lower() == fact_obj.lower()) or is_similar(obj.lower(), fact_obj.lower(), pos, embeddings_dict, threshold)):
                num_obj_matched += 1
                break

    return num_obj_matched == len(objs)


def match_ored_obj(obj, fact_obj_list, pos, threshold, victim_map, embeddings_dict):
    objs = obj.split('or')
    poses = pos.split()

    # sanity check
    assert len(objs) == len(poses)

    for i in range(len(objs)):
        obj = objs[i]
        pos = poses[i]
        for fact_obj in fact_obj_list:
            if ((fact_obj.lower() in victim_map and obj.lower() == victim_map[fact_obj.lower()]) or (
                    obj.lower() == fact_obj.lower()) or is_similar(obj.lower(), fact_obj.lower(), pos, embeddings_dict, threshold)):
                return True
    return False


def match_obj_pair_helper(obj_1, obj_1_pos, obj_2, obj_2_pos, fact_subjs, fact_objs, threshold, victim_map, embeddings_dict):
    # subj_matched = False
    # obj_matched = False
    if 'and' in obj_1 and 'and' in obj_2:
        subj_matched = match_anded_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_anded_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched and obj_matched

    elif 'and' in obj_1 and 'or' in obj_2:
        subj_matched = match_anded_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_ored_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'or' in obj_1 and 'and' in obj_2:
        subj_matched = match_ored_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_anded_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'or' in obj_1 and 'or' in obj_2:
        subj_matched = match_ored_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_ored_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'and' in obj_1:
        subj_matched = match_anded_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_obj_helper(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'or' in obj_1:
        subj_matched = match_ored_obj(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_obj_helper(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'and' in obj_2:
        subj_matched = match_obj_helper(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_anded_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    elif 'or' in obj_2:
        subj_matched = match_obj_helper(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_anded_obj(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched

    else:
        subj_matched = match_obj_helper(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
        obj_matched = match_obj_helper(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

        return subj_matched == obj_matched


# to match (subj, obj)
def match_obj_pair(verb, obj_1, obj_1_pos, obj_2, obj_2_pos, threshold, fact_type, table, victim_map, embeddings_dict):
    for f_type in table:
        if f_type == fact_type:
            fact = table[f_type]
            fact_verb = fact['kind'].lower()
            fact_verb = handle_verb_edge_cases(fact_verb, verb).lower()

            if (fact_verb == verb.lower() or is_similar(fact_verb, verb.lower(), 'verb', embeddings_dict,
                                                        threshold)) and 'subj' in fact and 'obj' in fact:
                fact_subj = fact['subj'].lower()
                fact_obj = fact['obj'].lower()

                fact_subjs = split_obj(fact_subj)

                fact_objs = split_obj(fact_obj)

                # print(fact_subjs)
                # print(fact_objs)

                is_matched = match_obj_pair_helper(obj_1, obj_1_pos, obj_2, obj_2_pos, fact_subjs, fact_objs, threshold,
                                                   victim_map, embeddings_dict)

                if is_matched:
                    return True
                else:
                    # check passive
                    if 'passive' in fact:
                        fact_subj = fact['obj'].lower()
                        fact_obj = fact['subj'].lower()

                        fact_subjs = split_obj(fact_subj)

                        fact_objs = split_obj(fact_obj)

                        if match_obj_pair_helper(obj_1, obj_1_pos, obj_2, obj_2_pos, fact_subjs, fact_objs, threshold,
                                                 victim_map, embeddings_dict):
                            return True

    return False


def contain_implicit_sex(obj, obj_pos, fact_obj, table, embeddings_dict, threshold):
    # check if obj in ['woman', 'man', 'female', 'male'] that implicity contains sex attribute
    # and fact_obj has an attribute of sex
    if (obj.lower() in ['woman', 'man', 'female', 'male'] or has_similar(obj.lower(),
                                                                         ['woman', 'man', 'female', 'male'], obj_pos, embeddings_dict,
                                                                         threshold)):
        for other_fact in table:
            key = list(other_fact.keys())[0]
            if key == 'person':
                if (other_fact[key]['kind'].lower() == fact_obj or is_similar(other_fact[key]['kind'].lower(), fact_obj,
                                                                              'noun', embeddings_dict, threshold)) and 'sex' in \
                        other_fact[key]:
                    return True
        return False
    return False


# check one is sex obj others not.. all cases
# all possible subjs and all possible objs
def match_implicit_sex_obj_pair(verb, obj_1, obj_1_pos, obj_2, obj_2_pos, threshold, fact_type, table, victim_map, embeddings_dict):
    for el in table:
        for f_type in el:
            if f_type == fact_type:
                fact = el[f_type]
                fact_verb = fact['kind'].lower()
                fact_verb = handle_verb_edge_cases(fact_verb, verb).lower()

                if (fact_verb == verb.lower() or is_similar(fact_verb, verb.lower(), 'verb', embeddings_dict,
                                                            threshold)) and 'subj' in fact and 'obj' in fact:
                    # sex, non_sex
                    fact_subj = fact['subj'].lower()
                    fact_obj = fact['obj'].lower()

                    fact_objs = split_obj(fact_obj)

                    sex_contained = contain_implicit_sex(obj_1, obj_1_pos, fact_subj, table, embeddings_dict, threshold)
                    is_matched = match_obj_helper(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

                    if sex_contained and is_matched:
                        return True
                    else:
                        if 'passive' in fact:
                            fact_subj = fact['obj'].lower()
                            fact_obj = fact['subj'].lower()

                            fact_objs = split_obj(fact_obj)

                            sex_contained = contain_implicit_sex(obj_1, obj_1_pos, fact_subj, table, embeddings_dict, threshold)
                            is_matched = match_obj_helper(obj_2, fact_objs, obj_2_pos, threshold, victim_map, embeddings_dict)

                            if sex_contained and is_matched:
                                return True

                    # sex, sex
                    fact_subj = fact['subj'].lower()
                    fact_obj = fact['obj'].lower()
                    sex_contained = contain_implicit_sex(obj_1, obj_1_pos, fact_subj, table, embeddings_dict, threshold)
                    sex_contained_2 = contain_implicit_sex(obj_2, obj_2_pos, fact_obj, table, embeddings_dict, threshold)

                    if sex_contained and sex_contained_2:
                        return True
                    else:
                        if 'passive' in fact:
                            fact_subj = fact['obj'].lower()
                            fact_obj = fact['subj'].lower()

                            sex_contained = contain_implicit_sex(obj_1, obj_1_pos, fact_subj, table, embeddings_dict, threshold)
                            sex_contained_2 = contain_implicit_sex(obj_2, obj_2_pos, fact_obj, table, embeddings_dict, threshold)

                            if sex_contained and sex_contained_2:
                                return True

                    # non_sex, sex
                    fact_subj = fact['subj'].lower()
                    fact_obj = fact['obj'].lower()

                    fact_subjs = split_obj(fact_subj)

                    is_matched = match_obj_helper(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
                    sex_contained = contain_implicit_sex(obj_2, obj_2_pos, fact_obj, table, embeddings_dict, threshold)

                    if is_matched and sex_contained:
                        return True
                    else:
                        if 'passive' in fact:
                            fact_subj = fact['obj'].lower()
                            fact_obj = fact['subj'].lower()

                            fact_subjs = split_obj(fact_subj)

                            is_matched = match_obj_helper(obj_1, fact_subjs, obj_1_pos, threshold, victim_map, embeddings_dict)
                            sex_contained = contain_implicit_sex(obj_2, obj_2_pos, fact_obj, table, embeddings_dict, threshold)

                            if is_matched and sex_contained:
                                return True

                    # non_sex, non_sex
                    fact_subj = fact['subj'].lower()
                    fact_obj = fact['obj'].lower()

                    fact_subjs = split_obj(fact_subj)

                    fact_objs = split_obj(fact_obj)

                    is_matched = match_obj_pair_helper(obj_1, obj_1_pos, obj_2, obj_2_pos, fact_subjs, fact_objs,
                                                       threshold, victim_map, embeddings_dict)

                    if is_matched:
                        return True
                    else:
                        # check passive
                        if 'passive' in fact:
                            fact_subj = fact['obj'].lower()
                            fact_obj = fact['subj'].lower()

                            fact_subjs = split_obj(fact_subj)

                            fact_objs = split_obj(fact_obj)

                            if match_obj_pair_helper(obj_1, obj_1_pos, obj_2, obj_2_pos, fact_subjs, fact_objs,
                                                     threshold, victim_map, embeddings_dict):
                                return True

    return False


def connected_by_coord_conj(token):
    coord_conjs = {"and", "but", "for", "nor", "or", "so", "yet"}
    for conj in coord_conjs:
        if conj in token:
            return conj
    return ''


def remove_indices(token):
    """
  Remove indices in a extracted token
  """
    if '_' in token:
        cleaned_token = []
        if ' ' in token:
            sub_toks = token.split()
            for sub_tok in sub_toks:
                if '_' in sub_tok:
                    sub_tok_name, sub_tok_idx = sub_tok.split('_')
                    cleaned_token.append(sub_tok_name)
                else:
                    cleaned_token.append(sub_tok)
        else:
            sub_tok_name, sub_tok_idx = token.split('_')
            cleaned_token.append(sub_tok_name)

        return ' '.join(cleaned_token)
    else:
        return token


def is_victim(noun, victim_map):
    if not noun in victim_map:
        return ''
    else:
        return victim_map[noun]


# count abstract facts & hypernyms & hyponyms
def count_fact_w_mods_from_table(table, embeddings_dict, threshold=0.8, mods=None):
    """
    Count objects with the given attributes from table
    mods (list): [('red', pos), ('blue', pos), ...] - mods used in summary
    """
    # ************* if count is not in the object's attrs, we can just count that as one **************
    # Add temporary count of 1 in case it says one!

    fact_obj_count = {}
    for fact in table:
        for key in fact:
            if key in ['person', 'object']:
                obj = fact[key]['kind']
                if mods:
                    mod_count = 0
                    for mod, mod_pos in mods:
                        fact_mods = list(fact[key].values())
                        if mod in fact_mods or has_similar(mod, fact_mods, mod_pos, embeddings_dict, threshold):
                            mod_count += 1
                    if mod_count == len(mods):
                        if 'count' in fact[key]:
                            if obj in fact_obj_count:
                                fact_obj_count[obj].append(fact[key]['count'])
                            else:
                                fact_obj_count[obj] = [fact[key]['count']]
                else:
                    # if mods == None, then we want the total count - total count of each main object always appears in the fact table!
                    if 'count' in fact[key]:
                        if obj in fact_obj_count:
                            fact_obj_count[obj].append(fact[key]['count'])
                        else:
                            fact_obj_count[obj] = [fact[key]['count']]
    return fact_obj_count


def filter_extracted_fact_w_mods(extracted_relation, embeddings_dict, threshold=0.8, mods=None):
    extracted_objs = {}
    for extracted_obj in extracted_relation:
        attrs = extracted_relation[extracted_obj]
        # filter out extracted facts that have all mods
        if mods:
            matched_attr_count = 0
            for attr in attrs:
                if attr[0][0] in mods or has_similar(attr[0][0], mods, attr[0][1], embeddings_dict, threshold):
                    matched_attr_count += 1
            if matched_attr_count == len(mods):
                # add all because we don't know if modifier is count or not
                # don't need to check if extracted_obj exists in the dict because it's unique for sure!
                extracted_objs[extracted_obj] = attrs
        else:
            extracted_objs[extracted_obj] = attrs

    return extracted_objs


def has_count_mods(modifiers):
    """
    Check if modifiers contain anything about counts and returns other mods
    """
    for modifier, modifier_found in modifiers:
        if modifier[0] in count_text_set:
            other_mods = [tuple(mod[0]) for mod in modifiers if mod[0][0] != modifier[0]]
            return (True, other_mods) if other_mods else (True, None)
    return (False, None)


def powerset(iterable):
    "powerset([1,2,3]) --> (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(2, len(s) + 1)))


def index_attr(attrs, target):
    for i in range(len(attrs)):
        src = attrs[i]
        if src[0][0] == target:
            return i
    # not found
    return -1


# deal with total count of an object (here the obj is hypernym of facts - more abstractive)!
def match_count_abstract_fact_helper(attrs, obj, count_fact, noun_synsets, adj_synsets, adv_synsets, verb_synsets, threshold):
    """
    count_fact: number of facts that have counts
    """
    # contains count text
    attr_set = set([attr[0][0] for attr in attrs])
    possible_counts = attr_set.intersection(count_text_set)

    # extracted_obj is hypernyms
    most_likely_obj = get_most_likely_synset(obj, 'noun', noun_synsets, adj_synsets, adv_synsets, verb_synsets)

    if possible_counts:
        print("While counting ... ")
        for possible_count in possible_counts:
            count_fact_synsets = []
            for fact_obj in count_fact:
                # check if fact_obj is the hyponym of extracted_obj (i.e. if it belongs to the category of extracted obj). For example, fact_obj = car, and obj = vehicle!
                most_likely_fact_obj = get_most_likely_synset(fact_obj, 'noun', noun_synsets, adj_synsets, adv_synsets, verb_synsets)
                if most_likely_fact_obj:
                    print(f'Likely synset - {most_likely_fact_obj} is found!!')
                    count_fact_synsets.append(most_likely_fact_obj)

            # every subsets of count fact synsets
            count_fact_power_sets = powerset(count_fact_synsets)

            for count_fact_power_set in count_fact_power_sets:
                similarities = get_similarity_to_lch(wn.synset(most_likely_obj), count_fact_power_set)

                if similarities:

                    similarity = min(similarities)
                    if similarity >= threshold:
                        print(
                            f'hypo-hypernym relation found between hypernym: {most_likely_obj} and hyponyms: {count_fact_power_set} with similarity of {similarity}!')
                        print(f'Similarities of each hyponyms to the hypernym are {similarities}')
                        print()

                        count = 0

                        for synset in count_fact_power_set:
                            obj_name = synset.split('.')[0]
                            fact_count = sum(
                                [int(num) if num.isdigit() else count_str_int_map[num] for num in count_fact[obj_name]])

                            count += fact_count

                        if possible_count == 'only':
                            if count == 1:
                                idx = index_attr(attrs, possible_count)
                                attrs[idx][1] = True
                                break

                        elif possible_count == 'couple':
                            if count == 2:
                                idx = index_attr(attrs, possible_count)
                                attrs[idx][1] = True
                                break

                        elif possible_count == 'a few':
                            if count <= 3:
                                idx = index_attr(attrs, possible_count)
                                attrs[idx][1] = True
                                break

                        elif possible_count in ['several', 'multiple']:
                            if count <= 5:
                                idx = index_attr(attrs, possible_count)
                                attrs[idx][1] = True
                                break

                        elif possible_count in ['many', 'a lot of', 'much', 'a number of', 'an amount of']:
                            if count >= 6:
                                idx = index_attr(attrs, possible_count)
                                attrs[idx][1] = True
                                break

                        else:
                            if possible_count.isdigit():
                                if count == int(possible_count):
                                    idx = index_attr(attrs, possible_count)
                                    attrs[idx][1] = True
                                    break

                            else:
                                if count == count_str_int_map[possible_count]:
                                    idx = index_attr(attrs, possible_count)
                                    attrs[idx][1] = True
                                    break


# hypernyms,
# get modifier and noun
# def match_count_abstract_fact(table, noun_modifiers, obj_counter, threshold=1/5, mods=None):
def match_count_abstract_fact(table, noun, modifiers, noun_synsets, adj_synsets, adv_synsets, verb_synsets, embeddings_dict, threshold=1 / 5, mods=None):
    """
    mods (list): modifiers to filter. Ex, [('red', 'ADJ'), ('black', 'ADJ')]
    """
    count_fact = count_fact_w_mods_from_table(table, embeddings_dict, mods=mods)

    # remove pos of mods in mods
    if mods:
        mods = [mod[0] for mod in mods]

    print(
        f"Matched fact in the source with count attributes: {count_fact} and that of extracted fact in the summary: ({noun}: {modifiers})!")

    if mods:
        obj_mods = [mod[0][0] for mod in modifiers]
        if set(obj_mods).intersection(set(mods)):
            match_count_abstract_fact_helper(modifiers, noun, count_fact, noun_synsets, adj_synsets, adv_synsets, verb_synsets, threshold)
    else:
        match_count_abstract_fact_helper(modifiers, noun, count_fact, noun_synsets, adj_synsets, adv_synsets, verb_synsets, threshold)


# TODO: add verb_obj!
def count_matched_fact(table, noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg, event_neg, event_modifiers, victim_map, embeddings_dict, noun_synsets, adj_synsets, adv_synsets, verb_synsets, threshold=0.8, synset_path_threshold=1/5):
    """

    :param table:
    :param noun_modifiers:
    :param obj_counter:
    :param subj_verb:
    :param verb_obj:
    :param subj_verb_obj:
    :param noun_neg:
    :param event_neg:
    :param event_modifiers:
    :param victim_map:
    :param threshold: threshold to detect if two words are similar based on wup_similarity and word2vec cosine similarity
    :param synset_path_threshold: threshold to detect hypernym/hyponym path similarities
    :return:
    """
    fact_count = 0
    obj_mod_counting = False
    obj_counter_counting = False

    for fact in table:
        # event
        # subj_verb, subj_verb_obj, verb_obj, event_neg, event_modifiers
        if list(fact.keys())[0] == 'event':
            fact_verb_ = fact['event']['kind'].lower()

            passive = 'passive' in fact['event']

            # verb_subj
            for verb, subjs in subj_verb.items():
                verb = remove_indices(verb)

                # TODO: move this to extractor
                coord_conj = connected_by_coord_conj(verb)
                if coord_conj:
                    print('************ here ************')
                    verb = ' '.join([morphy(verb, 'verb') for verb in verb.split(coord_conj)])

                fact_verb = handle_verb_edge_cases(fact_verb_, verb)

                if verb.lower() == fact_verb or is_similar(verb.lower(), fact_verb, 'verb', embeddings_dict, threshold): #or (fact_verb.con):  # are_synonyms(verb.lower(), fact_verb):
                    if 'subj' in fact['event']:
                        fact_subj = fact['event']['subj'].lower()
                        fact_obj = fact['event']['obj'].lower() if 'obj' in fact['event'] else None

                        subj_found = False
                        for subj in subjs:
                            subj_name = remove_indices(subj[0][0])
                            if not subj[1] and (subj_name.lower() == fact_subj or (
                                    fact_subj in victim_map and subj_name.lower() == victim_map[
                                fact_subj]) or is_similar(subj_name.lower(), fact_subj, subj[0][1], embeddings_dict, threshold)):
                                fact_count += 1
                                subj[1] = True
                                subj_found = True
                                break

                            # check if subj in ['woman', 'man', 'female', 'male'] that implicity contains sex attribute
                            # If so, go through the facts in the table and see if the subj has sex attribute
                            elif not subj[1] and (
                                    subj_name.lower() in ['woman', 'man', 'female', 'male'] or has_similar(
                                subj_name.lower(), ['woman', 'man', 'female', 'male'], subj[0][1], embeddings_dict, threshold)):

                                for other_fact in table:
                                    key = list(other_fact.keys())[0]
                                    if key == 'person':
                                        if (other_fact[key]['kind'].lower() == fact_subj or is_similar(
                                                other_fact[key]['kind'].lower(), fact_subj, 'noun', embeddings_dict,
                                                threshold)) and 'sex' in other_fact[key]:
                                            fact_count += 1
                                            subj[1] = True
                                            subj_found = True
                                            break

                                        elif passive and fact_obj and (
                                                other_fact[key]['kind'].lower() == fact_obj or is_similar(
                                            other_fact[key]['kind'].lower(), fact_obj, 'noun', embeddings_dict,
                                            threshold)) and 'sex' in other_fact[key]:
                                            fact_count += 1
                                            subj[1] = True
                                            subj_found = True
                                            break

                            elif passive and fact_obj:
                                if not subj[1] and (subj_name.lower() == fact_obj or (
                                        fact_obj in victim_map and subj_name.lower() == victim_map[
                                    fact_obj]) or is_similar(subj_name.lower(), fact_obj, subj[0][1], embeddings_dict, threshold)):
                                    fact_count += 1
                                    subj[1] = True
                                    subj_found = True
                                    break

                        if subj_found:
                            break

            # subj_verb_obj
            for verb, subj_obj_pairs in subj_verb_obj.items():
                verb = remove_indices(verb)
                for i in range(len(subj_obj_pairs)):
                    subj, obj = subj_obj_pairs[i][0]
                    if not subj_obj_pairs[i][1]:
                        subj_name = remove_indices(subj[0])
                        obj_name = remove_indices(obj[0])

                        is_matched = match_implicit_sex_obj_pair(verb, subj_name, subj[1], obj_name, obj[1], threshold,
                                                                 'event', table, victim_map, embeddings_dict)
                        if is_matched:
                            fact_count += 1
                            subj_obj_pairs[i][1] = True

            # verb_obj
            for verb, objs in verb_obj.items():
                verb = remove_indices(verb)

                fact_verb = handle_verb_edge_cases(fact_verb_, verb)

                if 'obj' in fact['event']:
                    fact_obj = fact['event']['obj'].lower()

                    for obj in objs:

                        if verb.lower() == fact_verb.lower() or is_similar(verb.lower(), fact_verb, 'verb', embeddings_dict, threshold):
                            obj_val, obj_pos = obj[0]
                            obj = remove_indices(obj_val)
                            conj = connected_by_coord_conj(obj)
                            if conj == 'or':
                                fact_obj_list = split_obj(fact_obj)
                                matched_ored = match_ored_obj(obj, fact_obj_list, obj_pos, threshold, victim_map, embeddings_dict)
                                if matched_ored:
                                    fact_count += 1
                                    obj[1] = True
                                    break

                            elif conj == 'and':
                                fact_obj_list = split_obj(fact_obj)
                                matched_anded = match_anded_obj(obj, fact_obj_list, obj_pos, threshold, victim_map, embeddings_dict)
                                if matched_anded:
                                    fact_count += 1
                                    obj[1] = True
                                    break

                            elif obj.lower() == fact_obj.lower() or is_similar(obj.lower(), fact_obj.lower(), 'noun', embeddings_dict, threshold) or contain_implicit_sex(obj, obj_pos, fact_obj, table, embeddings_dict, threshold):
                                fact_count += 1
                                obj[1] = True
                                break


            # event_neg
            for verb, negs in event_neg.items():
                verb = remove_indices(verb)

                fact_verb = handle_verb_edge_cases(fact_verb_, verb)
                if verb.lower() == fact_verb or is_similar(verb.lower(), fact_verb, 'verb', embeddings_dict, threshold):
                    for neg in negs:
                        if not neg[1] and 'neg' in fact['event']:
                            fact_count += 1
                            neg[1] = True
                            break

            # event modifiers
            for verb, modifiers in event_modifiers.items():
                verb = remove_indices(verb)

                # TODO: move this to extractor
                coord_conj = connected_by_coord_conj(verb)
                if coord_conj:
                    print('************ here ************')
                    verb = ' '.join([morphy(verb, 'verb') for verb in verb.split(coord_conj)])
                # if len(verb.split()) > 1:
                #   verb = ' '.join([morphy(verb.split()[0], 'verb'), *(verb.split()[1:])])

                fact_verb = handle_verb_edge_cases(fact_verb_, verb)

                include_phrase_mod = False

                if verb.lower() == fact_verb or is_similar(verb.lower(), fact_verb, 'verb', embeddings_dict, threshold):

                    # an object has a list of phrase modifiers
                    if 'phrase_mod' in fact['event'] and type(fact['event']['phrase_mod']) == list:
                        # splitted_phrase_mods = split_connected_words(fact['event']['phrase_mod'], prepositions)
                        fact_count += handle_modifiers(fact, 'event', verb, 'verb', modifiers, prepositions, threshold,
                                                       table, embeddings_dict, only_phrase_mod=True)
                        include_phrase_mod = True

                    for mod in modifiers:
                        # check subordinate
                        if type(mod[0][0]) == tuple:
                            # (main_subj, connective, sub_subj, sub_verb)
                            if 'sub_ord' in fact['event']:
                                # {'event': {'subj': 'arrest', 'kind': 'cam', 'sub_ord': 'after police respond'}},
                                fact_sub_clause = [fact['event']['subj']] + fact['event']['sub_ord'].split()

                                # TODO: check this !!!! and change it to store verb in its morphy
                                mod[0][0] = (*mod[0][0][:-1], *(mod[0][0][-1].split()))
                                # ('michael jackson', 'after', 'fight', 'broke out')

                                is_same = True
                                for i in range(len(mod[0][0])):
                                    word_1 = mod[0][0][i].lower()
                                    word_2 = fact_sub_clause[i].lower()
                                    if word_1 != word_2 and (
                                            word_2 not in prepositions and not is_similar(word_1, word_2, mod[0][1][i], embeddings_dict,
                                                                                          threshold)):
                                        is_same = False
                                        break

                                if is_same:
                                    fact_count += 1
                                    mod[1] = True

                        else:
                            # filter attributes based on the word's part of speech tag
                            attrs = filter_attrs(mod[0][1], fact, 'event', include_phrase_mod)
                            attrs = split_connected_words(attrs, prepositions)
                            fact_count += handle_modifiers_helper(mod, attrs, prepositions, embeddings_dict, threshold)

                # print('after')
                # print(verb, modifiers)
                # print(fact_verb, fact['event'])
                # print()


        # TODO: add modifier if it's used in the future
        elif list(fact.keys())[0] == 'modifier':
            pass

        # object
        else:
            # noun modifier, obj_counter, noun_neg
            # noun modifier
            for noun, modifiers in noun_modifiers.items():
                noun = remove_indices(noun)

                if not obj_mod_counting:
                    # count facts
                    has_count, other_mods = has_count_mods(modifiers)
                    if has_count:
                        match_count_abstract_fact(table, noun, modifiers, noun_synsets, adj_synsets, adv_synsets, verb_synsets, embeddings_dict, threshold=synset_path_threshold, mods=other_mods)

                include_phrase_mod = False
                if 'object' in fact and (noun.lower() == fact['object']['kind'].lower() or (
                        fact['object']['kind'].lower() in victim_map and noun.lower() == victim_map[
                    fact['object']['kind'].lower()]) or is_similar(noun.lower(), fact['object']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold)):
                    # an object has a list of phrase modifiers
                    if 'phrase_mod' in fact['object'] and type(fact['object']['phrase_mod']) == list:
                        # splitted_phrase_mods = split_connected_words(fact['object']['phrase_mod'], prepositions)
                        fact_count += handle_modifiers(fact, 'object', noun, 'noun', modifiers, prepositions, threshold,
                                                       table, embeddings_dict, only_phrase_mod=True)
                        include_phrase_mod = True
                    #   attrs = set(fact['object'][key] for key in fact['object'] if key != 'phrase_mod' and key != 'kind')
                    # else:
                    #   attrs = set(fact['object'][key] for key in fact['object'] if key != 'kind')

                    # attrs = split_connected_words(attrs, prepositions)

                    fact_count += handle_modifiers(fact, 'object', noun, 'noun', modifiers, prepositions, threshold,
                                                   table, embeddings_dict, include_phrase_mod=include_phrase_mod)

                #  noun.lower() == 'men': to handle case when men is used as a general term
                elif 'person' in fact and (noun.lower() == 'men' or (noun.lower() == fact['person']['kind'].lower() or (
                        fact['person']['kind'].lower() in victim_map and noun.lower() == victim_map[
                    fact['person']['kind'].lower()]) or is_similar(noun.lower(), fact['person']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold))):
                    # a person has a list of phrase modifiers
                    if 'phrase_mod' in fact['person'] and type(fact['person']['phrase_mod']) == list:
                        # splitted_phrase_mods = split_connected_words(fact['person']['phrase_mod'], prepositions)
                        fact_count += handle_modifiers(fact, 'person', noun, 'noun', modifiers, prepositions, threshold,
                                                       table, embeddings_dict, only_phrase_mod=True)
                        include_phrase_mod = True
                        # attrs = set(fact['person'][key] for key in fact['person'] if key != 'phrase_mod' and key != 'kind')
                    # else:
                    # attrs = set(fact['person'][key] for key in fact['person'] if key != 'kind')

                    # attrs = split_connected_words(attrs, prepositions)

                    fact_count += handle_modifiers(fact, 'person', noun, 'noun', modifiers, prepositions, threshold,
                                                   table, embeddings_dict, include_phrase_mod=include_phrase_mod)

                    # ----
                    # attrs = set(fact['person'].values())
                    # for mod in modifiers:
                    #   has_mod = mod[0][0].lower() in attrs

                    #   # check synonym
                    #   if not has_mod:
                    #     has_mod = has_similar(mod[0][0].lower(), attrs, mod[0][1])

                    #   if not mod[1] and has_mod:
                    #     fact_count += 1
                    #     mod[1] = True

            obj_mod_counting = True

            for obj, counters in obj_counter.items():
                obj = remove_indices(obj)

                if not obj_counter_counting:
                    # match_count
                    match_count_abstract_fact(table, obj, counters, noun_synsets, adj_synsets, adv_synsets, verb_synsets, embeddings_dict, synset_path_threshold)

                # if obj == 'men' and modifiers has 'count'
                # to handle when 'men' is used as a general termm for humans
                if obj.lower() == 'men':
                    counts = [counter for counter in counters if counter[0][1].lower() == 'num']

                    if len(counts) and 'person' in fact and 'count' in fact['person']:
                        for count in counts:
                            if not count[1] and count[0][0] == fact['person']['count']:
                                count[1] = True
                                fact_count += 1
                                break

                if 'object' in fact and (obj.lower() == fact['object']['kind'].lower() or (
                        fact['object']['kind'].lower() in victim_map and obj.lower() == victim_map[
                    fact['object']['kind'].lower()]) or is_similar(obj.lower(), fact['object']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold)):
                    for counter in counters:
                        if not counter[1] and 'count' in fact['object'] and fact['object']['count'] == counter[0][0]:
                            fact_count += 1
                            counter[1] = True
                            break

                elif 'person' in fact and (obj.lower() == fact['person']['kind'].lower() or (
                        fact['person']['kind'].lower() in victim_map and obj.lower() == victim_map[
                    fact['person']['kind'].lower()]) or is_similar(obj.lower(), fact['person']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold)):
                    for counter in counters:
                        if not counter[1] and 'count' in fact['person'] and fact['person']['count'] == counter[0][0]:
                            fact_count += 1
                            counter[1] = True
                            break
            obj_counter_counting = True

            # noun_neg
            for noun, negs in noun_neg.items():
                noun = remove_indices(noun)

                if 'object' in fact and (noun.lower() == fact['object']['kind'].lower() or (
                        fact['object']['kind'].lower() in victim_map and noun.lower() == victim_map[
                    fact['object']['kind'].lower()]) or is_similar(noun.lower(), fact['object']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold)):
                    for neg in negs:
                        if not neg[1] and 'neg' in fact['object']:
                            fact_count += 1
                            neg[1] = True
                            break

                elif 'person' in fact and (noun.lower() == fact['person']['kind'].lower() or (
                        fact['person']['kind'].lower() in victim_map and noun.lower() == victim_map[
                    fact['person']['kind'].lower()]) or is_similar(noun.lower(), fact['person']['kind'].lower(), 'noun', embeddings_dict,
                                                                   threshold)):
                    for neg in negs:
                        if not neg[1] and 'neg' in fact['person']:
                            fact_count += 1
                            neg[1] = True
                            break
    return fact_count