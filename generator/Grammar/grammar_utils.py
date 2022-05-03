from nltk.corpus import wordnet as wn


def get_next_day(date):
    if date.lower() == 'monday':
        return 'Tuesday'
    elif date.lower() == 'tuesday':
        return 'Wednesday'
    elif date.lower() == 'wednesday':
        return 'Thursday'
    elif date.lower() == 'thursday':
        return 'Friday'
    elif date.lower() == 'friday':
        return 'Saturday'
    elif date.lower() == 'saturday':
        return 'Sunday'
    elif date.lower() == 'sunday':
        return 'Monday'


def get_pos(pos):
    if pos == 'noun':
        pos = wn.NOUN
    elif pos == 'verb':
        pos = wn.VERB
    elif pos == 'adj':
        pos = wn.ADJ
    elif pos == 'adv':
        pos = wn.ADV
    else:
        pos = ''
    return pos

list_of_us_states = []