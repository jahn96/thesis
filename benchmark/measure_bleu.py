from nltk.translate.bleu_score import sentence_bleu


def measure_bleu(reference, candidate):
    score = sentence_bleu(reference, candidate)
    print(f"BLEU-4 score: {score * 100}")
    return score
