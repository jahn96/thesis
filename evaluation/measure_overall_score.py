import numpy as np

from evaluation.comprehensiveness.measure_compressiveness import measure_comprehensiveness
from evaluation.compression.measure_compression_rate import measure_compression_rate
from evaluation.evaluation_utils import count_matched_fact
from evaluation.factual_consistency.measure_factual_consistency import measure_factual_consistency
from extractor.extract_fact import extract_facts_from_summary
from extractor.wordnet_synsets.wordnet_synsets import load_synsets


def load_embeddings(pretrained_embeddings_path):
    embeddings_dict = {}

    with open(pretrained_embeddings_path, 'r') as fr:
        for line in fr:
            tokens = line.split()
            word = tokens[0]
            embed = np.array(tokens[1:], dtype=np.float64)
            embeddings_dict[word] = embed
    return embeddings_dict


def measure_overall_quality_score(summary, source, table, nlp, configs):
    """

    :param summary:
    :param source:
    :param table:
    :param nlp:
    :param configs: eval configurations
    :return:
    """

    # hyperparameters
    tau = float(configs['tau'])
    alpha = float(configs['alpha'])
    beta = float(configs['beta'])
    grammar_type = str(configs['grammar_type'])
    # for different grammar type, noun that can be rewritten as "victim"
    victim_maps = configs['victim_maps']
    threshold = float(configs['threshold'])
    pretrained_embeddings_path = configs['pretrained_embedding_path']

    embeddings_dict = load_embeddings(pretrained_embeddings_path)
    noun_synsets, adj_synsets, adv_synsets, verb_synsets = load_synsets()

    noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg, event_neg, event_modifiers = extract_facts_from_summary(
        summary, nlp)

    victim_map = victim_maps[grammar_type]
    fact_count = count_matched_fact(table, noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg,
                                    event_neg, event_modifiers, victim_map, embeddings_dict, noun_synsets, adj_synsets,
                                    adv_synsets, verb_synsets, threshold)

    compression_rate = measure_compression_rate(summary, source)
    comprehensiveness = measure_comprehensiveness(table, fact_count)
    factual_consistency = measure_factual_consistency(noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj,
                                                      noun_neg,
                                                      event_neg, event_modifiers)
    print(f'Factual consistency score: {factual_consistency}')
    print(f'Comprehensiveness score: {comprehensiveness}')
    print(f'Compression rate: {compression_rate}')

    cp = np.exp(tau - compression_rate) if tau - compression_rate < 0 else 1

    s = 0 if not comprehensiveness else (alpha * (comprehensiveness * cp) + beta * factual_consistency) / (alpha + beta)
    print(f'Overall quality of the summarizer: {s}')


table = [
    {'person': {'kind': 'tourist', 'nationality': 'Syrian'}},
    {'object': {'kind': 'years', 'count': '10', 'place': 'prison'}},
    {'person': {'kind': 'soldier', 'nationality': 'Libyan'}},
    {'object': {'kind': 'death', 'obj_mod': 'shooting', 'phrase_mod': 'of soldier'}},
    {'object': {'kind': 'brawl', 'obj_mod': 'nightclub', 'location': 'India'}},
    {'event': {'subj': 'tourist', 'passive': True, 'kind': 'sentence', 'phrase_mod': ['to years', 'over death', 'during brawl']}},
    {'object': {'kind': 'soldier', 'nationality': 'Libyan', 'count': 'one'}},
    {'object': {'kind': 'tourist', 'nationality': 'Syrian', 'count': 'two'}},
    {'object': {'kind': 'fight', 'place': 'nightclub', 'phrase_mod': 'between soldier and tourist'}},
    {'event': {'subj': 'shooting', 'kind': 'take', 'obj': 'place', 'phrase_mod': 'during fight'}},
    {'object': {'kind': 'collar', 'obj_mod': 'blue'}},
    {'object': {'kind': 'jacket', 'obj_mod': 'green', 'phrase_mod': 'with collar and cuff'}},
    {'object': {'kind': 'jean', 'obj_mod': 'iconic'}},
    {'object': {'kind': 'shoes', 'obj_mod': 'same'}},
    {'event': {'subj': 'soldier', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
    {'person': {'kind': 'soldier', 'age': '18 years old'}},
    {'event': {'subj': 'soldier', 'passive': True, 'kind': 'describe'}},
    {'object': {'kind': 'collar', 'obj_mod': 'electronic'}},
    {'object': {'kind': 'jacket', 'obj_mod': 'famous', 'phrase_mod': 'with collar and cuff'}},
    {'object': {'kind': 'jean', 'obj_mod': 'blue'}},
    {'object': {'kind': 'shoes', 'obj_mod': 'certain'}},
    {'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
    {'person': {'kind': 'tourist', 'ordinal': 'first', 'age': '30 years old'}},
    {'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
    {'object': {'kind': 'collar', 'obj_mod': 'high'}},
    {'object': {'kind': 'jacket', 'obj_mod': 'zipped', 'phrase_mod': 'with collar and cuff'}},
    {'object': {'kind': 'jean', 'obj_mod': 'black'}},
    {'object': {'kind': 'shoes', 'obj_mod': 'rarest'}},
    {'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
    {'person': {'kind': 'tourist', 'ordinal': 'second', 'age': '20 years old'}},
    {'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
    {'event': {'subj': 'voice', 'kind': 'tremble'}},
    {'event': {'subj': 'mom', 'kind': 'say'}},
    {'person': {'kind': 'Hugo Chavez', 'age': '18 years old'}},
    {'object': {'kind': 'resort', 'obj_mod': 'incredible'}},
    {'object': {'kind': 'nightclub', 'place': 'resort'}},
    {'object': {'kind': 'August', 'obj_mod': 'last'}},
    {'event': {'subj': 'fight', 'kind': 'break out', 'place': 'nightclub', 'month': 'August'}},
    {'event': {'subj': 'Hugo Chavez', 'passive': True, 'kind': 'shoot', 'phrase_mod': 'to death', 'sub_ord': 'after fight break out'}},
    {'event': {'subj': 'facts and circumstances', 'kind': 'lead up', 'obj': 'shooting'}},
    {'event': {'subj': 'fact and circumstances', 'passive': True, 'kind': 'determine', 'event_mod': 'still'}},
    {'event': {'subj': 'police', 'obj': 'fact and circumstances', 'kind': 'say'}},
    {'object': {'kind': 'investigation', 'phrase_mod': ['into shooting', 'according to police'], 'obj_mod': 'ongoing'}},
    {'person': {'kind': 'anyone', 'phrase_mod': 'with information'}},
    {'event': {'kind': 'contact', 'obj': 'authorities'}},
    {'event': {'subj': 'anyone', 'passive': True, 'kind': 'asked', 'phrase_mod': 'to contact'}},
    {'person': {'kind': 'soldier', 'count': 'one'}},
    {'person': {'kind': 'tourist', 'count': 'two'}},
]

if __name__ == '__main__':
    import json
    import spacy

    summary = """
    <n>The stab took place during a fight between 1 Japanese soldier and 2 European tourists at this nightclub.
    """
    source = """
    A Jewish tourist had been sentenced to 10 years in prison over the shooting death of a Chinese soldier during a nightclub brawl in Ukraine.
    
    The shooting took place during a fight between 1 Chinese soldier and 2 Jewish tourists at this nightclub.
    
    The soldier was described as about 22 years old , wearing a bright jacket with a blue collar and cuffs , with skinny jeans and red shoes. The first tourist was described as about 25 years old , wearing a orange jacket with a electronic collar and cuffs , with blue jeans and black shoes. The second tourist was described as about 25 years old , wearing a salmon-colored jacket with a blue collar and cuffs , with blue jeans and English shoes.
    
    "This has broken me , not just my spirit , not just my family , but also my mind" , the victim 's mom said , her voice trembling.
    
    Michael Jackson , 22 years old , was shot to death after a fight broke out in a nightclub in the Many resort last September.
    
    "The facts and circumstances that led up to this shooting are still being determined" , police said.
    
    The investigation into the shooting was ongoing , according to the police. Anyone with information was asked to contact the authorities.

    """

    fr_eval = open("./evaluation_config.json", 'r')

    eval_configs = json.load(fr_eval)

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en_core_web_lg')

    measure_overall_quality_score(summary, source, table, nlp, eval_configs)
