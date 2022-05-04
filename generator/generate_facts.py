import random
import ssl
from urllib.request import urlopen

import nltk
import pickle
import time

from generator.CrimeFactGenerator import CrimeFactGenerator
from generator.FactGenerator import FactGenerator
from generator.Grammar.Crime.AttorneyGrammar import AttorneyGrammar
from generator.Grammar.Crime.ClosingStatementGrammar import ClosingStatementGrammar
from generator.Grammar.Crime.CrimeReasonGrammar import CrimeReasonGrammar
from generator.Grammar.Crime.EventDescriptionGrammar import EventDescriptionGrammar
from generator.Grammar.Crime.EventHeadLineGrammar import EventHeadLineGrammar
from generator.Grammar.Crime.FamilyQuoteGrammar import FamilyQuoteGrammar
from generator.Grammar.Crime.NewsReleaseGrammar import NewsReleaseGrammar
from generator.Grammar.Crime.OutfitDescriptionGrammar import OutfitDescriptionGrammar
from generator.Grammar.Crime.PoliceReportGrammar import PoliceReportGrammar
from generator.Grammar.Crime.SceneDescriptionGrammar import SceneDescriptionGrammar
from generator.Grammar.Crime.SimilarEventGrammar import SimilarEventGrammar
from generator.Grammar.Crime.SurvivorQuoteGrammar import SurvivorQuoteGrammar
from generator.Grammar.Crime.SuspectDescriptionGrammar import SuspectDescriptionGrammar


def get_police_report_metadata(table, place, police_report_type=1):
    """
    It fills the metadata that is necessary to generate police report
    :param table:
    :param police_report_type:
    :return:
    """
    # metadata = {'place': random.choice(['restaurant', 'bar'])}
    metadata = {}

    for entry in table:
        for k, v in entry.items():
            if k == 'event':
                metadata['day'] = v['day'] if 'day' in v else ''
            elif k == 'object' and v['kind'] == place:
                metadata['place_mod'] = v['obj_mod']
                metadata['city'] = v['location'] if 'location' in v else ''
    return metadata

def get_event_location(table):
    metadata = {}

    for entry in table:
        for k, v in entry.items():
            if 'location' in v:
                metadata['location'] = v['location']
                break
        if 'location' in metadata:
            break
    return metadata


def get_basic_event_info(table, place):
    """
    It provides basic information about event such as place_mod, place, location, time, and day
    :param table:
    :return:
    """
    # metadata = {'place': random.choice(['restaurant', 'bar'])}
    metadata = {}
    for entry in table:
        for k, v in entry.items():
            if k == 'event':
                metadata['day'] = v['day'] if 'day' in v else ''
                metadata['time'] = v['time'] if 'time' in v else ''
            elif k == 'object' and v['kind'] == place:
                metadata['place_mod'] = v['obj_mod']
                metadata['location'] = v['location'] if 'location' in v else ''
    return metadata


def get_event_subhead_metadata(table):
    """
    It fills the metadata that is necessary to generate subheadline report
    :param table:
    :return:
    """
    metadata = {}
    for entry in table:
        for k, v in entry.items():
            if k == 'person':
                if v['kind'] == 'tourist':
                    metadata['tourist_nationality'] = v['nationality']
                elif v['kind'] == 'soldier':
                    metadata['soldier_nationality'] = v['nationality']

                if len(metadata) == 2:
                    break
    return metadata


def get_outfit_desc_metadata(table, victim):
    metadata = {}
    for entry in table:
        for k, v in entry.items():
            if k == 'person':
                if v['kind'] == victim and 'age' in v:
                    metadata['age'] = v['age']
                    return metadata
    return metadata


def create_template(template_type, grammar_type, template_meta):
    template = []
    if 'tense' not in template_meta:
        print('Please specify the tense of the grammar !')
        exit(-1)

    tense = template_meta['tense']

    num_text_int_map = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4
    }

    # Template 1
    # 1. Crime Event Description
    # 2. Scene Description
    # 3. Suspect Description
    # 4. Police Report

    # even though the template structure is same, the content and interaction between grammars
    # (metadata passed to subsequent grammar) are different
    if template_type == 1:

        if grammar_type == 1:
            # convert event in verb form to gerund (noun)
            event_verb_noun_map = {
                'mugged': 'mugging',
                'stabbed': 'stab',
                'knifed': 'stab'
            }

            # convert event in verb form to present participle (adj)
            event_verb_adj_map = {
                'mugged': 'mugging',
                'stabbed': 'stabbing',
                'knifed': 'stabbing'
            }

            event = random.choice(['mugged', 'stabbed', 'knifed'])

            if 'num_criminals' not in template_meta:
                print('Please specify the number of criminals to describe in the grammar')
                exit(-1)

            num_criminals = template_meta['num_criminals']
            event_place = random.choice(['restaurant', 'bar'])
            event_metadata = {'event': event, 'num_criminals': num_criminals, 'place': event_place}
            police_metadata = {'event': event_verb_noun_map[event], 'place': event_place}
            event_description_metadata = {'event': event_verb_noun_map[event], 'place': event_place}
            scene_description_metadata = {'event': event_verb_noun_map[event], 'place': event_place}
            closing_statement_metadata = {'event': event_verb_noun_map[event]}

            event_head_line_grammar = [EventHeadLineGrammar(tense, grammar_type, event_metadata)]
            scene_description_grammar = [SceneDescriptionGrammar(tense, grammar_type, scene_description_metadata)]

            outfit_grammar = [OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}) for i in
                              range(num_text_int_map[num_criminals])]

            police_grammar = [PoliceReportGrammar(tense, grammar_type, police_metadata)]
            event_description_grammar = [EventDescriptionGrammar(tense, grammar_type,
                                                                 event_description_metadata)]
            quote_grammar = [FamilyQuoteGrammar(tense, grammar_type, {})]
            closing_grammar = [ClosingStatementGrammar(tense, grammar_type, closing_statement_metadata)]

            suspect_desc_grammar = [SuspectDescriptionGrammar(tense, grammar_type, {})]

            rand_int = random.choice([1, 2])
            if rand_int == 1:
                template = [
                    event_head_line_grammar,
                    event_description_grammar,
                    outfit_grammar,
                    quote_grammar,
                    scene_description_grammar,
                    police_grammar,
                    suspect_desc_grammar,
                    closing_grammar,
                ]
            else:
                template = [
                    event_head_line_grammar,
                    event_description_grammar,
                    outfit_grammar,
                    quote_grammar,
                    scene_description_grammar,
                    police_grammar,
                    closing_grammar,
                ]

        elif grammar_type == 2:

            # convert event in verb form to gerund (noun)
            event_verb_noun_map = {
                'shot': 'shooting',
                'stabbed': 'stab'
            }

            # convert event in verb form to present participle (adj)
            event_verb_adj_map = {
                'shot': 'shooting',
                'stabbed': 'stabbing'
            }

            event = random.choice(['shot', 'stabbed'])

            if 'num_soldiers' not in template_meta:
                print('Please specify the number of soldiers to describe in the grammar')
                exit(-1)

            if 'num_tourists' not in template_meta:
                print('Please specify the number of tourists to describe in the grammar')
                exit(-1)

            num_soldiers = template_meta['num_soldiers']
            num_tourists = template_meta['num_tourists']
            event_metadata = {'event': event_verb_adj_map[event]}
            event_desc_metadata = {'event': event_verb_noun_map[event], 'num_soldiers': num_soldiers, 'num_tourists': num_tourists}
            police_metadata = {'event': event_verb_noun_map[event]}
            closing_statement_metadata = {'event': event_verb_noun_map[event]}
            attorney_metadata = {'event': event_verb_adj_map[event], 'num_attackers': num_tourists, 'location': 'nightclub'}
            crime_reason_metadata = {'event': event_verb_noun_map[event], 'num_attackers': num_text_int_map[num_tourists]}

            if num_text_int_map[num_soldiers] > 1:
                outfit_grammar = [OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}, obj='soldier') for i
                                  in range(num_text_int_map[num_soldiers])]
            else:
                outfit_grammar = [OutfitDescriptionGrammar(tense, grammar_type, obj='soldier')]

            if num_text_int_map[num_tourists] > 1:
                for i in range(num_text_int_map[num_tourists]):
                    outfit_grammar.append(OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}, obj='tourist'))
            else:
                outfit_grammar.append(OutfitDescriptionGrammar(tense, grammar_type, obj='tourist'))

            event_head_line_grammar = [EventHeadLineGrammar(tense, grammar_type, event_metadata)]
            event_description_grammar = [EventDescriptionGrammar(tense, grammar_type, event_desc_metadata)]
            attorney_grammar = [AttorneyGrammar(tense, grammar_type, attorney_metadata)]
            scene_description_grammar = [SceneDescriptionGrammar(tense, grammar_type, {'event': event})]
            police_grammar = [PoliceReportGrammar(tense, grammar_type, police_metadata)]

            quote_grammar = [FamilyQuoteGrammar(tense, grammar_type, {})]
            closing_grammar = [ClosingStatementGrammar(tense, grammar_type, closing_statement_metadata)]

            crime_reason_grammar = [CrimeReasonGrammar(tense, grammar_type, crime_reason_metadata)]

            news_release_grammar = [NewsReleaseGrammar(tense, grammar_type, {'event': event_verb_noun_map[event]})]

            survivor_quote_grammar = [SurvivorQuoteGrammar(tense, grammar_type, {})]
            similar_event_grammar = [SimilarEventGrammar(tense, grammar_type, {'event': event_verb_noun_map[event]})]

            template = [
                event_head_line_grammar,
                event_description_grammar,
                outfit_grammar,
                scene_description_grammar,
                attorney_grammar,
                quote_grammar,
                police_grammar,
                news_release_grammar,
                survivor_quote_grammar,
                crime_reason_grammar,
                closing_grammar,
                similar_event_grammar,
            ]

        elif grammar_type == 3:
            if 'num_killed' not in template_meta:
                print('Please specify the number of people killed')
                exit(-1)

            if 'num_injured' not in template_meta:
                print('Please specify the number of people injured')
                exit(-1)

            num_killed = template_meta['num_killed']
            num_injured = template_meta['num_injured']

            event_metadata = {'event': 'shooting', 'num_killed': num_killed, 'num_injured': num_injured}
            event_head_line_grammar = [EventHeadLineGrammar(tense, grammar_type, event_metadata)]

            police_report_grammar = [PoliceReportGrammar(tense, grammar_type, {})]
            template = [event_head_line_grammar, police_report_grammar]

    return template


def generate_facts_helper(generator: FactGenerator, template_type: int, grammar_type: int, metadata: dict):
    template = create_template(template_type, grammar_type, metadata)

    table = []
    texts = []

    # To update the metadata that would be passed to subsequent grammars
    police_metadata = {}
    event_description_metadata = {}
    got_victim_age = False
    scene_description_metadata = {}
    similar_event_metadata = {}

    for grammar_objs in template:
        paragraph = []
        for grammar_obj in grammar_objs:
            if isinstance(grammar_obj, PoliceReportGrammar):
                grammar_obj.metadata = {**grammar_obj.metadata, **police_metadata}
            elif isinstance(grammar_obj, EventDescriptionGrammar):
                grammar_obj.metadata = {**grammar_obj.metadata, **event_description_metadata}
            elif isinstance(grammar_obj, SceneDescriptionGrammar):
                grammar_obj.metadata = {**grammar_obj.metadata, **event_description_metadata, **scene_description_metadata}
            elif isinstance(grammar_obj, SimilarEventGrammar):
                grammar_obj.metadata = {**grammar_obj.metadata, **similar_event_metadata}

            grammar_obj.define_grammar()

            grammar = grammar_obj.grammar
            abstract_fact = grammar_obj.abstract_fact

            if not grammar:
                continue

            if type(grammar) == list:
                assert type(grammar) == type(abstract_fact)
                assert len(grammar) == len(abstract_fact)
                for i in range(len(grammar)):
                    sub_grammar = grammar[i]
                    sub_abs_fact = abstract_fact[i]
                    text = generator.generate_text(sub_grammar, sub_abs_fact, table)
                    paragraph.append(text)
            else:
                text = generator.generate_text(grammar, abstract_fact, table)
                paragraph.append(text)

            if isinstance(grammar_obj, EventHeadLineGrammar):
                if grammar_type == 1:
                    place = grammar_obj.metadata['place']
                    police_metadata.update(get_police_report_metadata(table, place))
                    event_description_metadata.update(get_basic_event_info(table, place))
                elif grammar_type == 2:
                    event_description_metadata.update(get_event_subhead_metadata(table))
                    similar_event_metadata.update(get_event_location(table))

            if grammar_type == 2:
                if isinstance(grammar_obj, OutfitDescriptionGrammar) and not got_victim_age:
                    scene_description_metadata.update(get_outfit_desc_metadata(table, 'soldier'))
                    got_victim_age = True

        if paragraph:
            texts.append(' '.join(paragraph))

    return texts, table


# TODO: add more grammar and template!
# TODO: check if the superlative comes with 'the'. Ex, the best
# TODO: organize schema

def generate_facts(num_articles, num_samples, write_to_file=False, print_generated_file=False):
    """

    :param num_articles: the number of articles to generate
    :param num_samples: the number of samples to write to a file
    :param write_to_file:
    :param print_generated_file:
    :return:
    """
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

    # fetch data
    ssl._create_default_https_context = ssl._create_unverified_context

    url = 'https://users.csc.calpoly.edu/~foaad/jayahn/models/noun_mod_occurrences.pkl'
    noun_mod_occurrences = pickle.load(urlopen(url))
    url = 'https://users.csc.calpoly.edu/~foaad/jayahn/models/named_entities_dist.pkl'
    named_entities_dist = pickle.load(urlopen(url))

    # TODO: preprocess these mined data!!!
    # TODO: rename generator with the better name

    # create data generator
    generator = CrimeFactGenerator(named_entities_dist, noun_mod_occurrences)

    # hyper parameters
    tense = 'past'
    num_criminals = 'three'
    num_soldiers = 'one'
    num_tourists = 'two'
    num_killed = 'one'
    num_injured = 'four'

    all_articles = []
    all_tables = []
    start_time = time.time()

    # num_articles = 1 # the number of articles to generate
    for i in range(num_articles):
        grammar_type = random.choice(range(1, 3))
        # grammar_type = 2
        template_type = 1

        # metadata_map = {template_type: {grammar_type: metadata}}
        metadata_map = {1: {1: {'tense': tense, 'num_criminals': num_criminals},
                            2: {'tense': tense, 'num_soldiers': num_soldiers, 'num_tourists': num_tourists},
                            3: {'tense': tense, 'num_killed': num_killed, 'num_injured': num_injured}}}

        texts, tables = generate_facts_helper(generator, template_type, grammar_type, metadata_map[template_type][grammar_type])

        # ***** Add total count attribute to the main object if its total count does not appear in the fact tree! Like Below: *****
            # if grammar_type == 1:
            #     tables.append({'person': {'kind': 'criminal', 'count': num_criminals}})
            # elif grammar_type == 2:
            #     tables.append({'person': {'kind': 'soldier', 'count': num_soldiers}})
            #     tables.append({'person': {'kind': 'tourist', 'count': num_tourists}})
        # ***** Add count attribute to the main object with unique modifier if its count does not appear in the fact tree! *****

        synthetic_data = '\n\n'.join(texts)

        all_articles.append(synthetic_data)
        all_tables.append(tables)

        if print_generated_file:
            print(synthetic_data)
            print()

            for table in tables:
                print(str(table) + ',')
            print()
    print(f"Time it took to generate {num_articles} articles: {time.time() - start_time} seconds.")

    if write_to_file:
        # num_samples = 10
        random_indices = random.sample(range(0, num_articles), num_samples)

        with open('randomly_chosen_articles.txt', 'w') as fw:
            for i in range(len(random_indices)):
                rand_idx = random_indices[i]
                article = all_articles[rand_idx]
                fw.write(str(i + 1) + '. ')
                fw.write(article + '\n')
                fw.write('\n')
                fw.write('\n')

        with open('randomly_chosen_facts.txt', 'w') as fw:
            for i in range(len(random_indices)):
                rand_idx = random_indices[i]
                table = all_tables[rand_idx]
                fw.write(str(i + 1) + '.\n')
                for fact in table:
                    fw.write(str(fact) + '\n')
                fw.write('\n')

    return all_articles, all_tables

    # print(tables)
    # print((synthetic_data, tables))

    # articles = []
    # for i in range(len(texts)):
    #     text = texts[i]
    #     synthetic_data = ' '.join(text)
    #     articles.append((synthetic_data, tables[i]))
    #
    # print(articles)


if __name__ == '__main__':
    num_articles = 100
    num_samples = 10
    generate_facts(num_articles, num_samples, write_to_file=True)
