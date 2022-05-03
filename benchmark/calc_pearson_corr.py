from scipy.stats import pearsonr


def calculate_pearson_corr(human_judgement, model_judgement):
    correlation, p_value = pearsonr(human_judgement, model_judgement)

    return correlation, p_value
