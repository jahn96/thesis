from nltk.corpus import wordnet as wn

count_int_str_map = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine',
                     10: 'ten'}
count_str_int_map = {'only': 1, 'couple': 2, 'a few': 3, 'several': 4, 'many': 5, 'a lot of': 5, 'an amount of': 5,
                     'multiple': 2, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
                     'eight': 8, 'nine': 9, 'ten': 10}
count_text_set = {'many', 'multiple', 'several', 'only', 'a lot of', 'much', 'a number of', 'an amount of', 'couple',
                  'a few', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', '1', '2', '3',
                  '4', '5', '6', '7', '8', '9', '10'}

prepositions = {'according to', 'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around', 'at',
                    'before', 'behind', 'between', 'beyond', 'but', 'by', 'concerning', 'despite', 'down', 'during',
                    'except', 'following', 'for', 'from', 'in', 'including', 'into', 'like', 'near', 'of', 'off', 'on',
                    'onto', 'out', 'over', 'past', 'plus', 'since', 'throughout', 'to', 'towards', 'under', 'until',
                    'up', 'upon', 'up to', 'with', 'within', 'without'}

conjunctions = {'and', 'or'}

months = {'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December'}

days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}

be_verbs = {'are', 'were', 'is', 'was', 'am'}

wh_words = {'where', 'when', 'why', 'how'}

list_of_places = {'bar', 'restaurant', 'nightclub'} # https://www.reddit.com/r/DnDBehindTheScreen/comments/3ih4jc/collection_of_place_nouns/

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

    if pos.lower() == 'sconj':
        return word

    if pos.lower() == 'num':
        return word

    # to ignore word that starts with number such as 20s
    if pos.lower() == 'noun' and not word.isalpha() and word.isalnum():
        return word

    # if word is propernoun or pronoun
    if pos.lower() in ['propn', 'pron']:
        return word.lower()

    wn_pos = get_pos(pos)
    if not wn_pos:
        print('unrecognized pos!')
        return word
        # print('unrecognized pos!')
        # print(word, pos)
        # exit(-1)

    # if word is a compound (or has two tokens)
    if len(word.split()) > 1:
        if word.split()[0] in prepositions:
            return ' '.join(word.split()[1:])

        if word.split()[-1] not in prepositions:
            return word.lower()

        res = []
        for tok in word.split():
            morphy_tok = wn.morphy(tok.lower(), wn_pos)
            if morphy_tok:
                res.append(morphy_tok)
            else:
                res.append(tok.lower())
        return ' '.join(res)

    # to handle gerund
    if word.endswith('ing') and pos.lower() == 'noun':
        return wn.morphy(word.lower(), wn.VERB)

    res = wn.morphy(word.lower(), wn_pos)

    if not res:
        return word.lower()
    else:
        return res
