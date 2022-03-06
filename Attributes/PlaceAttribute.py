# from Attributes.Attribute import Attribute
#
#
# class PlaceAttribute(Attribute):
#     def __init__(self):
#         super().__init__()
#         self.pattern = '[PLACE]'
#
#     def generate_attr(self, obj, noun_mod_occurrences, named_entities_dist, metadata):
#         if 'place' in metadata:
#             return {metadata['place']: 1}
#         return {'restaurant': 1, 'bar': 1, 'lounge': 1}
