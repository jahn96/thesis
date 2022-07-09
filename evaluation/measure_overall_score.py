import numpy as np

from evaluation.comprehensiveness.measure_compressiveness import measure_comprehensiveness
from evaluation.compression.measure_compression_rate import measure_compression_rate
from evaluation.evaluation_utils import count_matched_fact
from evaluation.factual_consistency.measure_factual_consistency import measure_factual_consistency
from extractor.extract_fact import extract_facts_from_summary
from analyzer.wordnet_synsets.wordnet_synsets import load_synsets


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

if __name__ == '__main__':
    import json
    import spacy

    summary = """
        Abu Romneys, 18 years old, was stabbed to death after a fight broke out in a nightclub in the all-inclusive resort last August.
    """
    source = """
        An American tourist had been sentenced to 10 years in prison over the stabbing death of a British soldier during a nightclub brawl in Pakistan.

The stab took place during a fight between one British soldier and two American tourists at this nightclub.

The soldier was described as about 18 years old, wearing a green jacket with a Chinese collar and cuffs, with blue jeans and big shoes. The first tourist was described as about 59 years old, wearing a striped jacket with a blue collar and cuffs, with black jeans and pink shoes. The second tourist was described as about 35 years old, wearing a light-colored jacket with a pink collar and cuffs, with blue jeans and sensible shoes.

Abu Romneys, 18 years old, was stabbed to death after a fight broke out in a nightclub in the all-inclusive resort last August.

The victim's attorney said on Tuesday "my client did not do anything to bring about the trouble and was attacked by two people stabbing at him at the nightclub."

"Our lives are completely destroyed.", the victim's mom said, wiping tears.

"The facts and circumstances that led up to this stab are still being determined.", police said. "We are trying to piece everything together." Police are asking for the cooperation of the public to come forward and help us with the investigation. The police chief earlier called the incident heartbreaking. Investigators are collecting evidence from the crime scene, officials said.

"It was scary. We were just trying to get to safety," a witness said.

Investigators are still working to determine what led up to the stab. They, however, said some altercation occurred when stab were happened. Police believe the motive for the stab is connected to an ongoing dispute between the suspect and the victim. Two knives have been seized that were used in the stab.

Anyone with information was asked to contact the authorities.
    """

    fr_eval = open("./evaluation_config.json", 'r')

    eval_configs = json.load(fr_eval)

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en_core_web_lg')

    measure_overall_quality_score(summary, source, table, nlp, eval_configs)
