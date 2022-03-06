# from Attributes.Attribute import Attribute
#
#
# class OrdinalAttribute(Attribute):
#     def __init__(self):
#         super().__init__()
#         self.pattern = '[OBJ_ORD]'
#         self.num_ordinal_map = {
#             1: 'first',
#             2: 'second',
#             3: 'third'
#         }
#
#     def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist):
#         ordinal = self.num_ordinal_map[metadata['ordinal']]
#         return {ordinal: 1}
