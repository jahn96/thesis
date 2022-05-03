from evaluation.evaluation_utils import count_total_fact


def measure_comprehensiveness(table, fact_count):
    # measure comprehensiveness
    total_fact = count_total_fact(table)

    comprehensiveness = fact_count / total_fact
    return comprehensiveness

#
# if __name__ == "__main__":
#     grammar_type = 2
#
#     # for different grammar type, noun that can be rewritten as "victim"
#     victim_maps = {
#         1: {},
#         2: {
#             'soldier': 'victim'
#         }
#     }
#
#     victim_map = victim_maps[grammar_type]
#     fact_count = count_matched_fact(table, noun_modifiers, obj_counter, subj_verb, verb_obj, subj_verb_obj, noun_neg, event_neg, event_modifiers, victim_map)
#
#     pass
