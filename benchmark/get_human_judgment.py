import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from benchmark.calc_pearson_corr import calculate_pearson_corr


def print_corr(corrs):
    corr_str = []
    for corr in corrs:
        corr_str.append(str(corr[0].round(3)))
    print(' & '.join(corr_str))


def get_human_fc_com_weights():
    # factual consistency and comprehensiveness weighting
    columns = range(10, len(records_df.columns) - 1, 10)
    fc_com_weights = records_df.loc[:, columns]
    fc_com_weights.columns = ['art_1_summ_1_w', 'art_1_summ_2_w', 'art_1_summ_3_w',
                              'art_2_summ_1_w', 'art_2_summ_2_w', 'art_2_summ_3_w',
                              'art_3_summ_1_w', 'art_3_summ_2_w', 'art_3_summ_3_w']
    # fc_com_weights = fc_com_weights.iloc[1:].reset_index(drop=True)

    fc_com_weights_res = []

    for i in range(len(fc_com_weights.columns)):
        column = fc_com_weights.columns[i]
        important_factor = records_df.loc[:, (i + 1) * 10 - 1]
        fc_com_weights_list = fc_com_weights[column].str.split(":")

        temp_res = []
        for j in range(len(fc_com_weights_list)):
            if len(fc_com_weights_list.iloc[j]) < 2:
                w_1, w_2 = records_df.loc[j, (i + 1) * 10 + 1].split(":")
            else:
                w_1, w_2 = fc_com_weights_list.iloc[j]

            if important_factor[j].lower() == 'comprehensiveness':
                temp_res.append([w_2.strip(), w_1.strip()])
            else:
                temp_res.append([w_1.strip(), w_2.strip()])

        fc_com_weights_res.extend(temp_res)

    fc_com_weights_df = pd.DataFrame(data=fc_com_weights_res, columns=['fc', 'com'])
    fc_com_weights_df = fc_com_weights_df.astype('float32')
    print((fc_com_weights_df.mean(axis=0) / 100).round(2))


def measure_fc_corr(write=False):
    columns = range(6, len(records_df.columns) - 1, 10)
    fc_rates = records_df.loc[:, columns]
    fc_rates.columns = ['art_1_summ_1_fc', 'art_1_summ_2_fc', 'art_1_summ_3_fc',
                        'art_2_summ_1_fc', 'art_2_summ_2_fc', 'art_2_summ_3_fc',
                        'art_3_summ_1_fc', 'art_3_summ_2_fc', 'art_3_summ_3_fc']

    for column in fc_rates.columns:
        for key, val in response_map.items():
            fc_rates[column] = fc_rates[column].str.replace(str(key), str(val))

    fc_rates = fc_rates.astype('float32')

    if write:
        with open('factual_consistency.txt', 'w') as fw:
            for column in fc_rates.columns:
                fw.write(", ".join(list(fc_rates[column].astype('str').values)) + '\n')

    fc_rates_res = (fc_rates.mean(axis=0) / 4).round(3)
    print(fc_rates_res)
    print(' & '.join(list(fc_rates_res.astype('str').values)))

    rouge_1 = [0.286, 0.279, 0.186, 0.259, 0.302, 0.259, 0.154, 0.283, 0.276]
    rouge_2 = [0.085, 0.080, 0.053, 0.082, 0.128, 0.082, 0.024, 0.087, 0.108]
    rouge_l = [0.246, 0.274, 0.169, 0.218, 0.278, 0.222, 0.141, 0.262, 0.241]
    bleu = [0.013, 0.034, 0.000, 0.036, 0.077, 0.025, 0.000, 0.036, 0.039]
    bert = [0.890, 0.896, 0.890, 0.866, 0.879, 0.887, 0.851, 0.869, 0.891]
    our_fc = [0.167, 0.923, 0.600, 1.000, 0.889, 0.727, 0.100, 0.889, 0.700]

    rouge_1_corr = calculate_pearson_corr(fc_rates_res, rouge_1)
    rouge_2_corr = calculate_pearson_corr(fc_rates_res, rouge_2)
    rouge_l_corr = calculate_pearson_corr(fc_rates_res, rouge_l)
    bleu_corr = calculate_pearson_corr(fc_rates_res, bleu)
    bert_corr = calculate_pearson_corr(fc_rates_res, bert)
    ours_corr = calculate_pearson_corr(fc_rates_res, our_fc)

    print_corr([rouge_1_corr, rouge_2_corr, rouge_l_corr, bleu_corr, bert_corr, ours_corr])
    print(rouge_1_corr)
    print(rouge_2_corr)
    print(rouge_l_corr)
    print(bleu_corr)
    print(bert_corr)
    print(ours_corr)


def measure_com_corr(write=False):
    # how comprehensive
    columns = range(7, len(records_df.columns) - 1, 10)
    com_rates = records_df.loc[:, columns]
    com_rates.columns = ['art_1_summ_1_com', 'art_1_summ_2_com', 'art_1_summ_3_com',
                         'art_2_summ_1_com', 'art_2_summ_2_com', 'art_2_summ_3_com',
                         'art_3_summ_1_com', 'art_3_summ_2_com', 'art_3_summ_3_com']
    # com_rates = com_rates.iloc[1:].reset_index(drop=True)

    for column in com_rates.columns:
        for key, val in response_map.items():
            com_rates[column] = com_rates[column].str.replace(str(key), str(val))

    com_rates = com_rates.astype('float32')

    if write:
        with open('compressiveness.txt', 'w') as fw:
            for column in com_rates.columns:
                fw.write(", ".join(list(com_rates[column].astype('str').values)) + '\n')

    com_rates_res = (com_rates.mean(axis=0) / 4).round(3)
    print(com_rates_res)
    print(' & '.join(list(com_rates_res.astype('str').values)))

    rouge_1 = [0.286, 0.279, 0.186, 0.259, 0.302, 0.259, 0.154, 0.283, 0.276]
    rouge_2 = [0.085, 0.080, 0.053, 0.082, 0.128, 0.082, 0.024, 0.087, 0.108]
    rouge_l = [0.246, 0.274, 0.169, 0.218, 0.278, 0.222, 0.141, 0.262, 0.241]
    bleu = [0.013, 0.034, 0.000, 0.036, 0.077, 0.025, 0.000, 0.036, 0.039]
    bert = [0.890, 0.896, 0.890, 0.866, 0.879, 0.887, 0.851, 0.869, 0.891]
    our_com = [0.016, 0.098, 0.025, 0.192, 0.128, 0.064, 0.007, 0.113, 0.050]

    rouge_1_corr = calculate_pearson_corr(com_rates_res, rouge_1)
    rouge_2_corr = calculate_pearson_corr(com_rates_res, rouge_2)
    rouge_l_corr = calculate_pearson_corr(com_rates_res, rouge_l)
    bleu_corr = calculate_pearson_corr(com_rates_res, bleu)
    bert_corr = calculate_pearson_corr(com_rates_res, bert)
    ours_corr = calculate_pearson_corr(com_rates_res, our_com)

    print_corr([rouge_1_corr, rouge_2_corr, rouge_l_corr, bleu_corr, bert_corr, ours_corr])
    print(rouge_1_corr)
    print(rouge_2_corr)
    print(rouge_l_corr)
    print(bleu_corr)
    print(bert_corr)
    print(ours_corr)


def measure_qual_corr(write=False):
    # how good is a summary is based on three criteria
    columns = [8, 18, 28, 38, 48, 58, 68, 78, 88]
    how_good_summary = records_df.loc[:, columns]
    how_good_summary.columns = ['art_1_summ_1', 'art_1_summ_2', 'art_1_summ_3',
                                'art_2_summ_1', 'art_2_summ_2', 'art_2_summ_3',
                                'art_3_summ_1', 'art_3_summ_2', 'art_3_summ_3']

    how_good_summary = how_good_summary.astype('float32')

    if write:
        with open('qual.txt', 'w') as fw:
            for column in how_good_summary.columns:
                fw.write(", ".join(list(how_good_summary[column].astype('str').values)) + '\n')

    how_good_summary = how_good_summary - 1  # because it's rated from 1 to 5 but we want from 0 to 4
    quality_human_judgments = (how_good_summary.mean(axis=0) / 4).round(3)
    print(quality_human_judgments)
    print(' & '.join(list(quality_human_judgments.astype('str').values)))

    rouge_1 = [0.286, 0.279, 0.186, 0.259, 0.302, 0.259, 0.154, 0.283, 0.276]
    rouge_2 = [0.085, 0.080, 0.053, 0.082, 0.128, 0.082, 0.024, 0.087, 0.108]
    rouge_l = [0.246, 0.274, 0.169, 0.218, 0.278, 0.222, 0.141, 0.262, 0.241]
    bleu = [0.013, 0.034, 0.000, 0.036, 0.077, 0.025, 0.000, 0.036, 0.039]
    bert = [0.890, 0.896, 0.890, 0.866, 0.879, 0.887, 0.851, 0.869, 0.891]
    our_q = [0.092, 0.511, 0.312, 0.592, 0.505, 0.396, 0.054, 0.499, 0.375]
    our_q_hum_w = [0.093, 0.519, 0.318, 0.600, 0.512, 0.402, 0.054, 0.507, 0.381]

    rouge_1_corr = calculate_pearson_corr(quality_human_judgments, rouge_1)
    rouge_2_corr = calculate_pearson_corr(quality_human_judgments, rouge_2)
    rouge_l_corr = calculate_pearson_corr(quality_human_judgments, rouge_l)
    bleu_corr = calculate_pearson_corr(quality_human_judgments, bleu)
    bert_corr = calculate_pearson_corr(quality_human_judgments, bert)
    ours_corr = calculate_pearson_corr(quality_human_judgments, our_q)
    ours_hum_corr = calculate_pearson_corr(quality_human_judgments, our_q_hum_w)

    print_corr([rouge_1_corr, rouge_2_corr, rouge_l_corr, bleu_corr, bert_corr, ours_corr, ours_hum_corr])

    print(rouge_1_corr)
    print(rouge_2_corr)
    print(rouge_l_corr)
    print(bleu_corr)
    print(bert_corr)
    print(ours_corr)
    print(ours_hum_corr)


def measure_qual_star_corr(write=False):
    # how good is a summary in general
    columns = range(4, len(records_df.columns) - 1, 10)
    how_good_summary = records_df.loc[:, columns]
    how_good_summary.columns = ['art_1_summ_1', 'art_1_summ_2', 'art_1_summ_3',
                                'art_2_summ_1', 'art_2_summ_2', 'art_2_summ_3',
                                'art_3_summ_1', 'art_3_summ_2', 'art_3_summ_3']

    how_good_summary = how_good_summary.astype('float32')

    if write:
        with open('qual_star.txt', 'w') as fw:
            for column in how_good_summary.columns:
                fw.write(", ".join(list(how_good_summary[column].astype('str').values)) + '\n')

    how_good_summary = how_good_summary - 1  # because it's rated from 1 to 5 but we want from 0 to 4
    quality_human_judgments = (how_good_summary.mean(axis=0) / 4).round(3)
    print(quality_human_judgments)
    print(' & '.join(list(quality_human_judgments.astype('str').values)))

    rouge_1 = [0.286, 0.279, 0.186, 0.259, 0.302, 0.259, 0.154, 0.283, 0.276]
    rouge_2 = [0.085, 0.080, 0.053, 0.082, 0.128, 0.082, 0.024, 0.087, 0.108]
    rouge_l = [0.246, 0.274, 0.169, 0.218, 0.278, 0.222, 0.141, 0.262, 0.241]
    bleu = [0.013, 0.034, 0.000, 0.036, 0.077, 0.025, 0.000, 0.036, 0.039]
    bert = [0.890, 0.896, 0.890, 0.866, 0.879, 0.887, 0.851, 0.869, 0.891]
    our_q = [0.092, 0.511, 0.312, 0.592, 0.505, 0.396, 0.054, 0.499, 0.375]
    our_q_hum_w = [0.093, 0.519, 0.318, 0.600, 0.512, 0.402, 0.054, 0.507, 0.381]

    rouge_1_corr = calculate_pearson_corr(quality_human_judgments, rouge_1)
    rouge_2_corr = calculate_pearson_corr(quality_human_judgments, rouge_2)
    rouge_l_corr = calculate_pearson_corr(quality_human_judgments, rouge_l)
    bleu_corr = calculate_pearson_corr(quality_human_judgments, bleu)
    bert_corr = calculate_pearson_corr(quality_human_judgments, bert)
    ours_corr = calculate_pearson_corr(quality_human_judgments, our_q)
    ours_hum_corr = calculate_pearson_corr(quality_human_judgments, our_q_hum_w)

    print_corr([rouge_1_corr, rouge_2_corr, rouge_l_corr, bleu_corr, bert_corr, ours_corr, ours_hum_corr])
    print(rouge_1_corr)
    print(rouge_2_corr)
    print(rouge_l_corr)
    print(bleu_corr)
    print(bert_corr)
    print(ours_corr)
    print(ours_hum_corr)


if __name__ == '__main__':
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open('Text Summarization Survey (Responses)')

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # get all the records of the data
    records_data = sheet_instance.get_all_values()

    # convert the json to dataframe
    records_df = pd.DataFrame.from_dict(records_data)

    # print(records_df.columns)

    # drop rows that are misleading
    rows_to_drop = [0, 19, 20, 22, 26]
    records_df = records_df.drop(rows_to_drop).reset_index(drop=True)

    response_map = {
        "Disagree": 0,
        "Somewhat disagree": 1,
        "Neutral": 2,
        "Somewhat agree": 3,
        "Agree": 4
    }

    get_human_fc_com_weights()
    print("-" * 30)
    measure_fc_corr()
    measure_com_corr()
    measure_qual_corr()
    measure_qual_star_corr()
