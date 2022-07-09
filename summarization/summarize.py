from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

import torch
from transformers import pipeline


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
