import argparse
import json

from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

import torch
from transformers import pipeline
import spacy
import sys

# TODO: distribution of compression rates from summarizers. Then, find the std and mean to normalize
# TODO: overall score - comprehensiveness * factuality score ...
#    -  if comprehensiveness is 0, then factuality is not important :(
#    - How do we justify the mathematical formula ??
#    - In addition, we were able to easily calculate the other aspects of summary such as comprehensiveness using fact-based approaches
from evaluation.measure_overall_score import measure_overall_quality_score
from generator.generate_facts import generate_facts


def bart_summarize(sources, model_name, max_length, min_length):
    summaries = []
    summarizer = pipeline("summarization", model=model_name)

    output_summaries = summarizer(sources, max_length=max_length, min_length=min_length, do_sample=False)

    for output_summary in output_summaries:
        summaries.append(output_summary['summary_text'])
    return summaries


def pegasus_summarize(sources, model_name):
    summaries = []
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

    for source in sources:
        src_text = [source]
        batch = tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt").to(device)
        translated = model.generate(**batch)
        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        summaries.append(tgt_text[0])
    return summaries


def t5_summarize(sources, model_name, max_length):
    summaries = []
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    for source in sources:
        input_ids = tokenizer.encode(source, return_tensors="pt", add_special_tokens=True)

        generated_ids = model.generate(input_ids=input_ids, num_beams=2, max_length=max_length,
                                       repetition_penalty=2.5, length_penalty=1.0, early_stopping=True)

        preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in
                 generated_ids]
        summaries.append(preds[0])
    return summaries


def summarize(model_name: str, fine_tuned_data: str, sources: list, max_length: int = 150,
              min_length: int = 30) -> list:
    if fine_tuned_data == 'cnn/dm':
        if model_name == 'facebook/bart-large-cnn':
            bart_summaries = bart_summarize(sources, model_name, max_length, min_length)
            return bart_summaries

        elif model_name == 'google/pegasus-cnn_dailymail':
            pegasus_summaries = pegasus_summarize(sources, model_name)
            return pegasus_summaries

        elif model_name == 'bochaowei/t5-small-finetuned-cnn-wei1':
            t5_summaries = t5_summarize(sources, model_name, max_length)
            return t5_summaries

        else:
            print(f"This evaluation system doesn't support {model_name} summarization model :(")
            exit(-1)

    elif fine_tuned_data == 'xsum':
        if model_name == 'facebook/bart-large-xsum':
            bart_summaries = bart_summarize(sources, model_name, max_length, min_length)
            return bart_summaries

        elif model_name == 'google/pegasus-xsum':
            pegasus_summaries = pegasus_summarize(sources, model_name)
            return pegasus_summaries

        elif model_name == 'aseda/t5-small-finetuned-xsum':
            t5_summaries = t5_summarize(sources, model_name, max_length)
            return t5_summaries

        else:
            print(f"This evaluation system doesn't support {model_name} summarization model :(")
            exit(-1)

    else:
        print(
            f"This evaluation system doesn't support {model_name} fine-tuned on {fine_tuned_data}! It only supports cnn/dm and xsum datasetes!")
        exit(-1)


# 'threshold for word sense disambiguation to check \
#                               if an attribute/object is appeared as a verb/noun in a fact in the output summary.'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process config files.')

    parser.add_argument('--config_file', default='config.json',
                        help="path to a main config file")

    parser.add_argument('--eval_config_file', default='./evaluation/evaluation_config.json',
                        help="path to a evaluation config file")

    args = parser.parse_args()

    cfg_path = args.config_file
    eval_cfg_path = args.eval_config_file

    fr = open(cfg_path, 'r')
    fr_eval = open(eval_cfg_path, 'r')

    configs = json.load(fr)
    eval_configs = json.load(fr_eval)

    model_name = configs['model_name']
    fine_tuned_data = configs['fine_tuned_data']

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en_core_web_lg')

    all_articles, all_fact_tables = generate_facts(print_generated_file=True)

    print('Loading a summarizer ....')
    summaries = summarize(model_name, fine_tuned_data, all_articles)

    for summary, article, table in zip(summaries, all_articles, all_fact_tables):
        measure_overall_quality_score(summary, article, table, nlp, eval_configs)

    fr.close()
    fr_eval.close()
