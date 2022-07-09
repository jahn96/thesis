# importing the required libraries
import json
import re

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from summarization.summarize import summarize

if __name__ == '__main__':
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open('Text summarization survey sheet')

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # get all the records of the data
    records_data = sheet_instance.get_all_records()

    # convert the json to dataframe
    records_df = pd.DataFrame.from_dict(records_data)

    summary_column = 'In your own words write a summary of the article above in 3-5 sentences. Do not use the same sentences, or sentence fragments from the article. '
    article_num_column = 'Actual Article Number'
    human_summaries = records_df.loc[records_df['Good_or_bad'] == 'Good'][[article_num_column, summary_column]]
    human_summaries.columns = ['article_num', 'human_summary']

    human_summaries = human_summaries.loc[human_summaries['article_num'].isin(['Article1', 'Article5', 'Article3'])]

    articles = human_summaries['article_num']

    article_texts = {}
    with open('../generator/randomly_chosen_articles.txt', 'r') as fr:
        # get articles
        article_text = ''
        key = '1'
        for line in fr:
            temp = re.match(r'\d+\.', line)
            if temp:
                new_key = temp.group().strip()[:-1]
                if key != new_key and new_key:
                    article_texts[key] = article_text
                    key = new_key
                    article_text = ''
            else:
                article_text += line

        if article_text:
            article_texts[key] = article_text

    model_name = 'aseda/t5-small-finetuned-xsum'
    fine_tuned_data = 'xsum'

    # get summaries
    t5_summaries = {}
    for key in article_texts:
        article_text = article_texts[key]
        summary = summarize(model_name, fine_tuned_data, [article_text])
        t5_summaries[key] = summary[0]

    model_name = 'google/pegasus-xsum'
    fine_tuned_data = 'xsum'

    # get summaries
    pega_summaries = {}
    for key in article_texts:
        article_text = article_texts[key]
        summary = summarize(model_name, fine_tuned_data, [article_text])
        pega_summaries[key] = summary[0]

    model_name = 'facebook/bart-large-cnn'
    fine_tuned_data = 'cnn/dm'
    # get summaries
    bart_summaries = {}
    for key in article_texts:
        article_text = article_texts[key]
        summary = summarize(model_name, fine_tuned_data, [article_text])
        bart_summaries[key] = summary[0]

    ordered_articles_1 = []
    ordered_summaries_pega = []
    ordered_summaries_bart = []
    ordered_summaries_t5 = []

    for article_num in human_summaries['article_num']:
        article_num = article_num[len('Article'):].strip()
        ordered_summaries_pega.append(pega_summaries[article_num])
        ordered_summaries_bart.append(bart_summaries[article_num])
        ordered_summaries_t5.append(t5_summaries[article_num])
        ordered_articles_1.append(article_texts[article_num])

    human_summaries['pega_system_summary'] = ordered_summaries_pega
    human_summaries['bart_system_summary'] = ordered_summaries_bart
    human_summaries['t5_system_summary'] = ordered_summaries_t5

    human_summaries['article_texts'] = ordered_articles_1

    human_summaries.to_csv('eval_summaries.csv')
    # measure ROUGE and BLEU
    pass


    # article_links = []
    # for article in articles:
    #     article_links.append(records_df[article][0])

    # read randomly chosen articles.txt and get the article
    # run it thorugh summarizer and get system summaries
    # calc rouge