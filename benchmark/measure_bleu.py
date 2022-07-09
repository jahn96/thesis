import nltk.tokenize
from nltk.translate.bleu_score import corpus_bleu


def measure_bleu(reference, candidate):
    tokens_refs = [nltk.tokenize.word_tokenize(reference)]
    tokens_cands = [nltk.tokenize.word_tokenize(candidate)]

    score = corpus_bleu([tokens_refs], tokens_cands)
    print(f"BLEU-4 score: {score}")
    return score

if __name__ == '__main__':
    reference = 'The shooting took place during a fight between one Irish soldier and two Russian tourists.<n>The soldier was described as about 22 years old, wearing a gray jacket.<n>The first tourist was described as about 41 years old, wearing a gray jacket.<n>The second tourist was described as about 44 years old, wearing a denim jacket.'
    candidate = 'The article is about a shooting that happened involving a Russian tourist and an Irish solider that happened in a nightclub in Cambodia. The Irish solider was shot after a fight broke out at the club, and when the police arrived there was several people running away. What led up to the shooting is still largely undetermined, however, police believe the motive was connected to an altercation between the offender and victim.'

    reference = 'I am on the vacation.'
    candidate = 'I am not on the vacation.'
    measure_bleu(reference, candidate)
