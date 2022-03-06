from nltk.tokenize import word_tokenize


def measure_compression_rate(summary, source):
    summary_tokens = word_tokenize(summary)
    source_tokens = word_tokenize(source)

    return len(summary_tokens) / len(source_tokens) # * 100
