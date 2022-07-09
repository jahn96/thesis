import pandas as pd

from benchmark.measure_bleu import measure_bleu
from benchmark.measure_rouge import measure_rouge


def write_rouge_bleu():
    df = pd.read_csv('./eval_summaries.csv')
    print(df)
    print(df.columns)

    pega_rouge1_scores = []
    pega_rouge2_scores = []
    pega_rougel_scores = []
    pega_bleu_scores = []

    bart_rouge1_scores = []
    bart_rouge2_scores = []
    bart_rougel_scores = []
    bart_bleu_scores = []

    t5_rouge1_scores = []
    t5_rouge2_scores = []
    t5_rougel_scores = []
    t5_bleu_scores = []

    for _, row in df[['human_summary', 'pega_system_summary', 'bart_system_summary', 't5_system_summary']].iterrows():
        human_summary = row['human_summary']

        pega_sys_summary = row['pega_system_summary']
        bart_sys_summary = row['bart_system_summary']
        t5_sys_summary = row['t5_system_summary']

        rouge_score = measure_rouge(human_summary, pega_sys_summary)[0]
        rouge1 = rouge_score['rouge-1']['r']
        rouge2 = rouge_score['rouge-2']['r']
        rougel = rouge_score['rouge-l']['r']

        pega_rouge1_scores.append(rouge1)
        pega_rouge2_scores.append(rouge2)
        pega_rougel_scores.append(rougel)

        bleu_score = measure_bleu(human_summary, pega_sys_summary)
        pega_bleu_scores.append(bleu_score)

        # bart
        rouge_score = measure_rouge(human_summary, bart_sys_summary)[0]
        rouge1 = rouge_score['rouge-1']['r']
        rouge2 = rouge_score['rouge-2']['r']
        rougel = rouge_score['rouge-l']['r']

        bart_rouge1_scores.append(rouge1)
        bart_rouge2_scores.append(rouge2)
        bart_rougel_scores.append(rougel)

        bleu_score = measure_bleu(human_summary, bart_sys_summary)
        bart_bleu_scores.append(bleu_score)

        # t5
        rouge_score = measure_rouge(human_summary, t5_sys_summary)[0]
        rouge1 = rouge_score['rouge-1']['r']
        rouge2 = rouge_score['rouge-2']['r']
        rougel = rouge_score['rouge-l']['r']

        t5_rouge1_scores.append(rouge1)
        t5_rouge2_scores.append(rouge2)
        t5_rougel_scores.append(rougel)

        bleu_score = measure_bleu(human_summary, t5_sys_summary)
        t5_bleu_scores.append(bleu_score)

    df['pega_rouge1_score'] = pega_rouge1_scores
    df['pega_rouge2_score'] = pega_rouge2_scores
    df['pega_rougel_score'] = pega_rougel_scores
    df['pega_bleu_score'] = pega_bleu_scores

    df['bart_rouge1_score'] = bart_rouge1_scores
    df['bart_rouge2_score'] = bart_rouge2_scores
    df['bart_rougel_score'] = bart_rougel_scores
    df['bart_bleu_score'] = bart_bleu_scores

    df['t5_rouge1_score'] = t5_rouge1_scores
    df['t5_rouge2_score'] = t5_rouge2_scores
    df['t5_rougel_score'] = t5_rougel_scores
    df['t5_bleu_score'] = t5_bleu_scores

    df.to_csv('./rouge_bleu.csv')


def get_scores():
    df = pd.read_csv('./rouge_bleu.csv')

    df = df.loc[df['article_num'].isin(['Article1', 'Article5', 'Article3'])]

    print(df.loc[df['article_num'] == 'Article1'].loc[:,
          ['pega_rouge1_score',
           'pega_rouge2_score',
           'pega_rougel_score',
           'pega_bleu_score',
           'bart_rouge1_score',
           'bart_rouge2_score',
           'bart_rougel_score',
           'bart_bleu_score',
           't5_rouge1_score',
           't5_rouge2_score',
           't5_rougel_score',
           't5_bleu_score']].mean(axis=0).round(3))


def get_human_summaries():
    df = pd.read_csv('./rouge_bleu.csv')

    df = df.loc[df['article_num'].isin(['Article1', 'Article5', 'Article3'])]

    for summ in df.loc[df['article_num'] == 'Article1'].loc[:, 'human_summary'].str.replace('\n', ''):
        print(summ)

    for summ in df.loc[df['article_num'] == 'Article1'].loc[:, 'pega_system_summary']:
        print(summ)

    for summ in df.loc[df['article_num'] == 'Article1'].loc[:, 'bart_system_summary']:
        print(summ)

    for summ in df.loc[df['article_num'] == 'Article1'].loc[:, 't5_system_summary']:
        print(summ)


if __name__ == '__main__':
    # write_rouge_bleu()
    # pd.options.display.max_colwidth = 1000
    # get_human_summaries()
    #
    get_scores()
