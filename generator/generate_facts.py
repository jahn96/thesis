import random
import ssl
from urllib.request import urlopen

import nltk
import pickle
from nltk.stem import PorterStemmer

from generator.CrimeFactGenerator import CrimeFactGenerator
from generator.Grammar.Crime.EventHeadLineGrammar import EventHeadLineGrammar
from generator.Grammar.Crime.EventSubHeadLineGrammar import EventSubHeadLineGrammar
from generator.Grammar.Crime.OutfitDescriptionGrammar import OutfitDescriptionGrammar
from generator.Grammar.Crime.PoliceReportGrammar import PoliceReportGrammar
from generator.Grammar.Crime.SceneDescriptionGrammar import SceneDescriptionGrammar


# # TODO: generate facts that would appear in an article?
#
# def get_location():
#     syns = wn.all_synsets(pos='n')
#     locations = set()
#
#     for syn in syns:
#         if 'location' in syn.lexname():
#             lemmas = syn.lemma_names()
#             locations = locations.union([lemma for lemma in lemmas if lemma[0].isupper()])
#
#     return list(locations)
#
#
# def get_data(attr):
#     if attr.lower() == 'location':
#         # html_doc = requests.get('https://en.wikipedia.org/wiki/List_of_municipalities_in_California').text
#         # bs = BeautifulSoup(html_doc, 'html.parser')
#         #
#         # list_of_cities_in_cal = [row.find('th').text.strip() for row in
#         #                          bs.select('.wikitable')[1].find('tbody').find_all('tr')[2:]]
#         # return list_of_cities_in_cal
#         return get_location()
#
#     elif attr.lower() == 'color':
#         # TODO: below code returns unusual colors which led to incorrect summarization
#         # html_doc = requests.get('https://en.wikipedia.org/wiki/List_of_colors:_A%E2%80%93F').text
#         # bs = BeautifulSoup(html_doc, 'html.parser')
#         #
#         # list_of_colors = [row.find('th').find('a').text.strip() for row in
#         #                   bs.select('.wikitable')[0].find('tbody').find_all('tr')[1:]]
#
#         list_of_colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'purple']
#         return list_of_colors
#
#     return []
#
#
# def fill_sentence(sent, fact):
#     """
#     This function fills attrs and obj with lexical items
#
#     Parameters:
#     sent (string): sentence generated based on a grammr
#     fact (dict): a fact that the sentence should contain
#
#     Returns:
#     string: a filled sentence
#
#     """
#     for key in fact:
#         sent = re.sub(re.escape("[" + key + "]"), fact[key], sent)
#     return sent
#
#
# def generate_fact(obj, attrs):
#     """
#     This function generates a fact about an object and its attributes
#
#     Parameters:
#     obj (string): a category of items such as ball, building, ...
#     attrs (list of string): a list of attributes an object has such as color, location, ...
#
#     Returns:
#     dict: fact about the given object with the given attributes
#
#     """
#
#     if len(attrs) == 0:
#         print('Attributes are not given!', file=sys.stderr)
#         exit(-1)
#
#     entry = {}
#
#     # retrieve items in a given object category from wordnet
#     item_lemmas = [lemma.name() for hyponym in wn.synset(obj + '.n.01').hyponyms() for lemma in hyponym.lemmas()]
#     item_lemma = random.choice(item_lemmas)
#
#     if '_' in item_lemma:
#         item_lemma = item_lemma.replace('_', ' ')
#
#     entry['obj'] = item_lemma
#     # fact_table['obj'].append(item_lemma)
#
#     for attr in attrs:
#         if attr == 'color':
#             list_of_colors = get_data(attr)
#             color = random.choice(list_of_colors).lower()
#             color = preprocess_item(color)
#             entry['color'] = color
#             # fact_table[attr].append(color)
#         elif attr == 'location':
#             list_of_locations = get_data(attr)
#             location = random.choice(list_of_locations)
#             location = preprocess_item(location)
#             entry['location'] = location
#             # fact_table[attr].append(location)
#     return entry
#
#
# def preprocess_item(item):
#     # remove hyphen
#     if "-" in item:
#         return re.sub(r"-", " ", item)
#     # remove parenthesis
#     elif len(re.findall(r' \(.*\)', item)) != 0:
#         return re.sub(r' \(.*\)', "", item)
#     return item


def get_police_report_metadata(table, police_report_type=1):
    metadata = {'place': 'restaurant'}

    for entry in table:
        for k, v in entry.items():
            if k == 'event':
                metadata['event'] = 'attack'
                metadata['day'] = v['day'] if 'day' in v else ''
            elif k == 'object' and metadata and v['kind'] == metadata['place']:
                metadata['place_mod'] = v['obj_mod']
                metadata['city'] = v['location'] if 'location' in v else ''
    return metadata


def get_event_subhead_metadata(table):
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


def create_template(generator, template_id, tense, grammar_type, num_criminals):
    # Template 1
    # 1. Crime Event Description
    # 2. Scene Description
    # 3. Suspect Description
    # 4. Police Report
    if template_id == 1:
        table = []
        texts = []

        # even though the template structure is same, the content and interaction between grammars
        # (metadata passed to subsequent grammar) are different
        if grammar_type == 1:
            event_metadata = {'event': random.choice(['mugged', 'stabbed'])}
            police_metadata = {}

            event_head_line_grammar = EventHeadLineGrammar(tense, grammar_type, num_criminals, event_metadata)
            outfit_grammar = [OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}) for i in
                              range(num_criminals)]
            police_grammar = PoliceReportGrammar(tense, grammar_type)

            template = [event_head_line_grammar, *outfit_grammar, police_grammar] # event_head_line_grammar, *outfit_grammar, police_grammar]

            for grammar_obj in template:
                if isinstance(grammar_obj, PoliceReportGrammar):
                    grammar_obj.metadata = police_metadata

                grammar_obj.define_grammar()

                grammar = grammar_obj.grammar
                abstract_fact = grammar_obj.abstract_fact
                generator.generate_data(grammar, abstract_fact, texts, table)

                if isinstance(grammar_obj, EventHeadLineGrammar):
                    police_metadata.update(get_police_report_metadata(table))

        elif grammar_type == 2:
            num_soldiers = 1
            num_tourists = 2
            event_subhead_metadata = {'num_soldiers': num_soldiers, 'num_tourists': num_tourists}

            outfit_grammar = [OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}, obj='soldier') for i in
                              range(num_soldiers)]

            for i in range(num_tourists):
                outfit_grammar.append(OutfitDescriptionGrammar(tense, grammar_type, {'ordinal': i + 1}, obj='tourist'))

            template = [
                EventHeadLineGrammar(tense, grammar_type, num_criminals),
                SceneDescriptionGrammar(tense, grammar_type),
                EventSubHeadLineGrammar(tense, grammar_type),
                *outfit_grammar,
                PoliceReportGrammar(tense, grammar_type)
            ]

            for grammar_obj in template:
                if isinstance(grammar_obj, EventSubHeadLineGrammar):
                    grammar_obj.metadata = event_subhead_metadata

                grammar_obj.define_grammar()

                grammar = grammar_obj.grammar
                abstract_fact = grammar_obj.abstract_fact
                generator.generate_data(grammar, abstract_fact, texts, table)

                if isinstance(grammar_obj, EventHeadLineGrammar):
                    event_subhead_metadata.update(get_event_subhead_metadata(table))

        return texts, table


# TODO: add more grammar and template!
# TODO: check if the superlative comes with 'the'. Ex, the best
# TODO: organize schema

def main():
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

    # create stemmer
    stemmer = PorterStemmer()

    # hyper parameters
    tense = 'past'
    num_criminals = 3

    # grammar_type = random.choice(range(1, 3))
    grammar_type = 2
    template_id = 1

    # define_template
    texts, tables = create_template(generator, template_id, tense, grammar_type, num_criminals)

    # num_data = 1
    # texts, tables = generate_text(generator, template, num_data)

    # print(len(texts))
    # print(len(tables))
    # assert len(texts) == len(tables)

    synthetic_data = ' '.join(texts)

    print(synthetic_data)

    # print(tables)

    for table in tables:
        print(table)
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
    main()
