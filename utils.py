from nltk.corpus import wordnet as wn

count_int_str_map = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine',
                     10: 'ten'}
count_str_int_map = {'only': 1, 'couple': 2, 'a few': 3, 'several': 4, 'many': 5, 'a lot of': 5, 'an amount of': 5,
                     'multiple': 2, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
                     'eight': 8, 'nine': 9, 'ten': 10}
count_text_set = {'many', 'multiple', 'several', 'only', 'a lot of', 'much', 'a number of', 'an amount of', 'couple',
                  'a few', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', '1', '2', '3',
                  '4', '5', '6', '7', '8', '9', '10'}

prepositions = {'according to', 'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around', 'at', 'before', 'behind', 'between', 'beyond', 'but', 'by', 'concerning', 'despite', 'down', 'during', 'except', 'following', 'for', 'from', 'in', 'including', 'into', 'like', 'near', 'of', 'off', 'on', 'onto', 'out', 'over', 'past', 'plus', 'since', 'throughout', 'to', 'towards', 'under', 'until', 'up', 'upon', 'up to', 'with', 'within', 'without'}


city_state_map = {
    'Seattle': 'Washington'
}


def get_pos(pos):
    if not pos:
        return pos

    pos = pos.lower()

    if pos == 'noun':
        pos = wn.NOUN
    elif pos in ['verb', 'aux']:
        pos = wn.VERB
    elif pos == 'adj':
        pos = wn.ADJ
    elif pos == 'adv':
        pos = wn.ADV
    else:
        pos = ''
    return pos


def morphy(word, pos):
    if not pos:
        return wn.morphy(word.lower(), None)

    if pos.lower() == 'num':
        return word

    # to ignore word that starts with number such as 20s
    if pos.lower() == 'noun' and not word.isalpha() and word.isalnum():
        return word

    # to handle gerund
    if word.endswith('ing') and pos.lower() == 'noun':
        return wn.morphy(word.lower(), wn.VERB)

    # if word is propernoun or pronoun
    if pos.lower() in ['propn', 'pron']:
        return word.lower()

    # if word is a compound (or has two tokens)
    if len(word.split()) > 1:
        return word.lower()

    wn_pos = get_pos(pos)
    if not wn_pos:
        print('unrecognized pos!')
        print(word, pos)
        exit(-1)

    return wn.morphy(word.lower(), wn_pos)
