from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from generator.generate_facts import generate_sentence
from evaluation.compression.measure_compression_rate import measure_compression_rate
import argparse
from transformers import pipeline
from evaluation.factual_consistency.srl2Tree import Srl2Tree
from nltk.tokenize import sent_tokenize
from evaluation.factual_consistency.extract_facts import get_srl, evaluate_facts
from evaluation.comprehensiveness.measure_compresiveness import QACov
import spacy
import sys
# TODO: distribution of compression rates from summarizers. Then, find the std and mean to normalize
# TODO: overall score - comprehensiveness * factuality score ...
#    -  if comprehensiveness is 0, then factuality is not important :(
#    - How do we justify the mathematical formula ??
#    - In addition, we were able to easily calculate the other aspects of summary such as comprehensiveness using fact-based approaches

def summarize(model_name: str, sources: list, max_length: int = 130, min_length: int = 30) -> list:
    summaries = []

    if model_name == 'facebook/bart-large-cnn':
        summarizer = pipeline("summarization", model=model_name)

        output_summaries = summarizer(sources, max_length=max_length, min_length=min_length, do_sample=False)

        for output_summary in output_summaries:
            summaries.append(output_summary['summary_text'])

    elif 'google/pegasus' in model_name:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        tokenizer = PegasusTokenizer.from_pretrained(model_name)
        model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

        for source in sources:
            src_text = [source]
            batch = tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt").to(device)
            translated = model.generate(**batch)
            tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
            summaries.append(tgt_text[0])
    else:
        print(f"This evaluation system doesn't support {model_name} summarization model :(")
        exit(-1)

    return summaries

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get object and attributes')
    parser.add_argument('object', metavar='object', type=str,
                        help='a category of objects in facts')

    parser.add_argument('attrs', nargs='+',
                        choices=['color', 'location'],
                        help='attributes of objects in facts')

    parser.add_argument('--threshold', default=0.8,
                        help='threshold for word sense disambiguation to check \
                              if an attribute/object is appeared as a verb/nounin a fact in the output summary.')

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en')
    args = parser.parse_args()

    category = args.object
    attributes = args.attrs
    threshold = args.threshold

    if not category:
        print('Category of objects must be provided!', file=sys.stderr)
        exit(-1)
    if not attributes:
        print('Attributes of objects must be provided!', file=sys.stderr)
        exit(-1)

    model_name = "facebook/bart-large-cnn"
    # model_name = "google/pegasus-cnn_dailymail"

    # generate facts
    sources, fact_table = generate_sentence('ball', ['color'], tense='present')
    print(fact_table)
    print(sources)

    sources = ["The cue ball is green. The tennis balls are yellow. The ping pong ball is orange."]
    fact_table = [{'obj': 'cue ball', 'color': 'green'}, {'obj': 'tennis ball', 'color': 'yellow'},
                  {'obj': 'ping pong ball', 'color': 'orange'}]

    max_length = max(len(nlp(source)) for source in sources) + 2
    # summarize generated facts
    summaries = summarize(model_name, sources, max_length=max_length)
    print(summaries)

    for summary in summaries:
        sents = sent_tokenize(summary)

        predictor = get_srl()

        fact_trees = []

        srl_to_tree_obj = Srl2Tree()

        num_consistent_fact = 0
        num_facts = 0

        # evaluate factual consistency
        for sent in sents:
            # extract facts from summaries
            srl_out = predictor.predict(sentence=sent)
            print(srl_out)

            words = srl_out['words']
            # tags = [tok.pos_ for tok in nlp(sent)]

            facts = srl_to_tree_obj.get_facts(srl_out)
            print(facts)

            factual_consistency = evaluate_facts(nlp, category, facts, words, fact_table, threshold)
            print(factual_consistency)
            if factual_consistency:
                num_consistent_fact += 1

        print('factual consistency score:', num_consistent_fact / len(sents))

    # compression_rate
    compression_rates = []

    # comprehensiveness
    qaCov = QACov()
    comprehensiveness_scores = []

    for summary, source in zip(summaries, sources):
        comprehensiveness_score = qaCov.compute_score(summary, source)
        comprehensiveness_scores.append(comprehensiveness_score)

        compression_rate = measure_compression_rate(summary, source)
        compression_rates.append(compression_rate)

    print('compression rates:', compression_rates)
    print('comprehensive scores:', comprehensiveness_scores)


    # Finetuned Pegasus with xsum dataset - Model size: 2.28G
    # xsum_model_name = 'google/pegasus-xsum'
    # device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # xsum_tokenizer = PegasusTokenizer.from_pretrained(xsum_model_name)
    # xsum_model = PegasusForConditionalGeneration.from_pretrained(xsum_model_name).to(device)

    # for text in texts:
    #     src_text = [text]
    #     batch = xsum_tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt").to(device)
    #     translated = xsum_model.generate(**batch)
    #     tgt_text = xsum_tokenizer.batch_decode(translated, skip_special_tokens=True)
    #     summaries.append(tgt_text[0])


    # facebook bart-large-cnn
    # summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # summaries = []
    # sents, fact_table = generate_sentence(category, attributes, tense='present', num_sentences=3)
    # print(fact_table)

    # texts = [' '.join(sents)]
    # print(texts)

    # print(summarizer(texts[0], max_length=130, min_length=30, do_sample=False))
    # print(summaries)
