import argparse
import json

import spacy
import time
import sys

# TODO: distribution of compression rates from summarizers. Then, find the std and mean to normalize
# TODO: overall score - comprehensiveness * factuality score ...
#    -  if comprehensiveness is 0, then factuality is not important :(
#    - How do we justify the mathematical formula ??
#    - In addition, we were able to easily calculate the other aspects of summary such as comprehensiveness using fact-based approaches
from evaluation.measure_overall_score import measure_overall_quality_score
from generator.generate_facts import generate_facts
from summarization.summarize import summarize

article_1 = """
An Israeli tourist had been sentenced to 10 years in prison over the shooting death of a French soldier during a nightclub brawl in the U.S.

The shooting took place during a fight between one French soldier and two Israeli tourists at this nightclub.

The soldier had no description. The first tourist was described as about 26 years old, wearing a light-colored jacket with a blue-collar and cuffs, with skinny jeans and big shoes. The second tourist was described as about 59 years old, wearing a gray jacket with a pink collar and cuffs, with blue jeans, and heavy shoes.

The victim's attorney said on Thursday "my client did not do anything to bring about the trouble and was attacked by two people shooting at him at the nightclub."

"This has broken me, not just my spirit, not just my family, but also my mind.", the victim's mom said, her voice trembling.

"The facts and circumstances that led up to this shooting are still being determined.", police said. "Unfortunately, we had shootings that occurred inside and outside the structure", the police told CNN on Monday. "We are trying to piece everything together." Police are asking for the cooperation of the public to come forward and help us with the investigation. The police chief earlier called the incident heartbreaking. Investigators are collecting evidence from the crime scene, officials said.

"As many as 10 rounds were fired inside, prompting some people to jump out the windows.", the news release said.

"It was scary. We were just trying to get to safety," a witness said.

Investigators are still working to determine what led up to the shooting. They, however, said some altercation occurred when gunshots were fired. Police believe the motive for the shooting is connected to an ongoing dispute between the suspect and the victim. Two handguns have been seized that were used in the shooting.

Anyone with information was asked to contact the authorities.
"""

fact_table_1 = [{'person': {'kind': 'tourist', 'nationality': 'Israeli'}},
{'object': {'kind': 'years', 'count': '10', 'place': 'prison'}},
{'person': {'kind': 'soldier', 'nationality': 'French'}},
{'object': {'kind': 'death', 'obj_mod': 'shooting', 'phrase_mod': 'of soldier'}},
{'object': {'kind': 'brawl', 'obj_mod': 'nightclub', 'location': 'the U.S.'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'sentence', 'phrase_mod': ['to years', 'over death', 'during brawl']}},
{'person': {'kind': 'soldier', 'nationality': 'French', 'count': 'one'}},
{'person': {'kind': 'tourist', 'nationality': 'Israeli', 'count': 'two'}},
{'object': {'kind': 'fight', 'place': 'nightclub', 'phrase_mod': 'between soldier and tourist'}},
{'event': {'subj': 'shooting', 'kind': 'take', 'obj': 'place', 'phrase_mod': 'during fight'}},
{'object': {'neg': True, 'kind': 'description'}},
{'event': {'subj': 'soldier', 'obj': 'description', 'kind': 'have'}},
{'object': {'kind': 'collar', 'obj_mod': 'blue'}},
{'object': {'kind': 'jacket', 'obj_mod': 'light-colored', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'skinny'}},
{'object': {'kind': 'shoes', 'obj_mod': 'big'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'first', 'age': '26 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'object': {'kind': 'collar', 'obj_mod': 'pink'}},
{'object': {'kind': 'jacket', 'obj_mod': 'gray', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'blue'}},
{'object': {'kind': 'shoes', 'obj_mod': 'heavy'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'second', 'age': '59 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'person': {'kind': 'attorney', 'obj_pos': 'victim'}},
{'event': {'kind': 'bring', 'phrase_mod': 'about trouble'}},
{'object': {'kind': 'anything', 'phrase_mod': 'to bring'}},
{'event': {'subj': 'client', 'neg': True, 'kind': 'do', 'obj': 'anything'}},
{'event': {'subj': 'people', 'obj': 'him', 'kind': 'shoot', 'location': 'nightclub'}},
{'person': {'kind': 'people', 'count': 'two'}},
{'event': {'subj': 'client', 'passive': True, 'kind': 'attack', 'obj': 'people'}},
{'event': {'subj': 'attorney', 'obj': 'client', 'kind': 'say', 'day': 'Thursday'}},
{'event': {'subj': 'voice', 'kind': 'tremble'}},
{'event': {'subj': 'mom', 'kind': 'say'}},
{'event': {'subj': 'fact and circumstances', 'passive': True, 'kind': 'determine', 'event_mod': 'still'}},
{'event': {'subj': 'police', 'obj': 'fact and circumstances', 'kind': 'say'}},
{'event': {'subj': 'shooting', 'kind': 'occur', 'phrase_mod': ['inside structure', 'outside structure']}},
{'event': {'subj': 'we', 'obj': 'shooting', 'kind': 'have'}},
{'event': {'subj': 'police', 'obj': 'CNN', 'kind': 'tell', 'day': 'Monday', 'sub_ord': 'that we have'}},
{'event': {'kind': 'piece', 'obj': 'everything', 'event_mod': 'together'}},
{'event': {'subj': 'we', 'kind': 'try', 'phrase_mod': 'to piece'}},
{'object': {'kind': 'cooperation', 'phrase_mod': 'of public'}},
{'event': {'kind': 'come', 'event_mod': 'forward'}},
{'event': {'kind': 'help', 'obj': 'us', 'phrase_mod': 'with investigation'}},
{'event': {'subj': 'police', 'kind': 'ask', 'phrase_mod_1': 'for cooperation', 'phrase_mod_2': 'to come and help'}},
{'person': {'kind': 'chief', 'obj_mod': 'police'}},
{'object': {'kind': 'incident', 'obj_mod': 'heartbreaking'}},
{'event': {'subj': 'chief', 'obj': 'incident', 'kind': 'call'}},
{'object': {'kind': 'scene', 'obj_mod': 'crime'}},
{'object': {'kind': 'evidence', 'phrase_mod': 'from scene'}},
{'event': {'subj': 'investigator', 'obj': 'evidence', 'kind': 'collect'}},
{'event': {'subj': 'official', 'obj': 'investigator', 'kind': 'say'}},
{'object': {'kind': '10', 'obj_mod': 'as many as'}},
{'object': {'kind': 'round', 'count': '10'}},
{'person': {'kind': 'people', 'count': 'some'}},
{'event': {'kind': 'jump out', 'obj': 'windows'}},
{'event': {'subj': 'round', 'kind': 'prompt', 'obj': 'people', 'phrase_mod': 'to jump out'}},
{'event': {'subj': 'round', 'passive': True, 'kind': 'fire', 'event_mod': 'inside'}},
{'event': {'subj': 'news release', 'obj': 'round', 'kind': 'say'}},
{'event': {'subj': 'witness', 'kind': 'say'}},
{'event': {'subj': 'what', 'kind': 'lead up', 'obj': 'shooting'}},
{'event': {'subj': 'investigator', 'kind': 'work', 'event_mod': 'still', 'phrase_mod': 'to determine'}},
{'event': {'subj': 'gunshot', 'passive': True, 'kind': 'fire'}},
{'event': {'subj': 'altercation', 'kind': 'occur', 'sub_ord': 'when gunshot fire'}},
{'event': {'subj': 'they', 'kind': 'say', 'event_mod': 'however'}},
{'object': {'kind': 'motive', 'phrase_mod': 'for shooting'}},
{'object': {'kind': 'dispute', 'obj_mod': 'ongoing', 'phrase_mod': 'between suspect and victim'}},
{'event': {'subj': 'motive', 'passive': True, 'kind': 'connect', 'phrase_mod': 'to dispute'}},
{'event': {'subj': 'police', 'obj': 'motive', 'kind': 'believe'}},
{'object': {'kind': 'handgun', 'count': 'two'}},
{'event': {'subj': 'handgun', 'passive': True, 'kind': 'use', 'phrase_mod': 'in shooting'}},
{'event': {'subj': 'handgun', 'passive': True, 'kind': 'seize'}},
{'person': {'kind': 'anyone', 'phrase_mod': 'with information'}},
{'event': {'kind': 'contact', 'obj': 'authorities'}},
{'event': {'subj': 'anyone', 'passive': True, 'kind': 'asked', 'phrase_mod': 'to contact'}}]

article_2 = """
A British tourist had been sentenced to 10 years in prison over the stabbing death of a Chinese soldier during a nightclub brawl in America.

The stab took place during a fight between one Chinese soldier and two British tourists at this nightclub.

The soldier was described as about 33 years old, wearing a red jacket with a blue collar and cuffs, with skinny jeans and Italian shoes. The first tourist was described as about 58 years old, wearing a big jacket with a blue collar and cuffs, with skinny jeans and black shoes. The second tourist was described as about 30 years old, wearing a salmon-colored jacket with a blue collar and cuffs, with blue jeans and athletic shoes.

Sanjay Gupta, 33 years old, was stabbed to death after a fight broke out in a nightclub in the expensive resort last September.

The victim's attorney said on Tuesday "my client did not do anything to bring about the trouble and was attacked by two people stabbing at him at the nightclub."

"Our lives are completely destroyed.", the victim's mom said, wiping tears.

"The facts and circumstances that led up to this stab are still being determined.", police said. "We are trying to piece everything together." Police are asking for the cooperation of the public to come forward and help us with the investigation. The police chief earlier called the incident heartbreaking. Investigators are collecting evidence from the crime scene, officials said.

"It was scary. We were just trying to get to safety," a witness said.

Investigators are still working to determine what led up to the stab. They, however, said some altercation occurred when the stab happened. Police believe the motive for the stab is connected to an ongoing dispute between the suspect and the victim. One knife has been seized that was used in the stab.

Anyone with information was asked to contact the authorities.
"""

fact_table_2 = [
{'person': {'kind': 'tourist', 'nationality': 'British'}},
{'object': {'kind': 'years', 'count': '10', 'place': 'prison'}},
{'person': {'kind': 'soldier', 'nationality': 'Chinese'}},
{'object': {'kind': 'death', 'obj_mod': 'stabbing', 'phrase_mod': 'of soldier'}},
{'object': {'kind': 'brawl', 'obj_mod': 'nightclub', 'location': 'America'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'sentence', 'phrase_mod': ['to years', 'over death', 'during brawl']}},
{'person': {'kind': 'soldier', 'nationality': 'Chinese', 'count': 'one'}},
{'person': {'kind': 'tourist', 'nationality': 'British', 'count': 'two'}},
{'object': {'kind': 'fight', 'place': 'nightclub', 'phrase_mod': 'between soldier and tourist'}},
{'event': {'subj': 'stab', 'kind': 'take', 'obj': 'place', 'phrase_mod': 'during fight'}},
{'object': {'kind': 'collar', 'obj_mod': 'blue'}},
{'object': {'kind': 'jacket', 'obj_mod': 'red', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'skinny'}},
{'object': {'kind': 'shoes', 'obj_mod': 'Italian'}},
{'event': {'subj': 'soldier', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'soldier', 'age': '33 years old'}},
{'event': {'subj': 'soldier', 'passive': True, 'kind': 'describe'}},
{'object': {'kind': 'collar', 'obj_mod': 'blue'}},
{'object': {'kind': 'jacket', 'obj_mod': 'big', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'skinny'}},
{'object': {'kind': 'shoes', 'obj_mod': 'black'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'first', 'age': '58 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'object': {'kind': 'collar', 'obj_mod': 'blue'}},
{'object': {'kind': 'jacket', 'obj_mod': 'salmon-colored', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'blue'}},
{'object': {'kind': 'shoes', 'obj_mod': 'athletic'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'second', 'age': '30 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'person': {'kind': 'Sanjay Gupta', 'age': '33 years old'}},
{'object': {'kind': 'resort', 'obj_mod': 'expensive'}},
{'object': {'kind': 'nightclub', 'place': 'resort'}},
{'object': {'kind': 'September', 'obj_mod': 'last'}},
{'event': {'subj': 'fight', 'kind': 'break out', 'place': 'nightclub', 'month': 'September'}},
{'event': {'subj': 'Sanjay Gupta', 'passive': True, 'kind': 'stab', 'phrase_mod': 'to death', 'sub_ord': 'after fight break out'}},
{'person': {'kind': 'attorney', 'obj_pos': 'victim'}},
{'event': {'kind': 'bring', 'phrase_mod': 'about trouble'}},
{'object': {'kind': 'anything', 'phrase_mod': 'to bring'}},
{'event': {'subj': 'client', 'neg': True, 'kind': 'do', 'obj': 'anything'}},
{'event': {'subj': 'people', 'obj': 'him', 'kind': 'stab', 'location': 'nightclub'}},
{'person': {'kind': 'people', 'count': 'two'}},
{'event': {'subj': 'client', 'passive': True, 'kind': 'attack', 'obj': 'people'}},
{'event': {'subj': 'attorney', 'obj': 'client', 'kind': 'say', 'day': 'Tuesday'}},
{'event': {'subj': 'mom', 'obj': 'tears', 'kind': 'wipe'}},
{'event': {'subj': 'mom', 'kind': 'say'}},
{'event': {'subj': 'fact and circumstances', 'passive': True, 'kind': 'determine', 'event_mod': 'still'}},
{'event': {'subj': 'police', 'obj': 'fact and circumstances', 'kind': 'say'}},
{'event': {'kind': 'piece', 'obj': 'everything', 'event_mod': 'together'}},
{'event': {'subj': 'we', 'kind': 'try', 'phrase_mod': 'to piece'}},
{'object': {'kind': 'cooperation', 'phrase_mod': 'of public'}},
{'event': {'kind': 'come', 'event_mod': 'forward'}},
{'event': {'kind': 'help', 'obj': 'us', 'phrase_mod': 'with investigation'}},
{'event': {'subj': 'police', 'kind': 'ask', 'phrase_mod_1': 'for cooperation', 'phrase_mod_2': 'to come and help'}},
{'person': {'kind': 'chief', 'obj_mod': 'police'}},
{'object': {'kind': 'incident', 'obj_mod': 'heartbreaking'}},
{'event': {'subj': 'chief', 'obj': 'incident', 'kind': 'call'}},
{'object': {'kind': 'scene', 'obj_mod': 'crime'}},
{'object': {'kind': 'evidence', 'phrase_mod': 'from scene'}},
{'event': {'subj': 'investigator', 'obj': 'evidence', 'kind': 'collect'}},
{'event': {'subj': 'official', 'obj': 'investigator', 'kind': 'say'}},
{'event': {'subj': 'witness', 'kind': 'say'}},
{'event': {'subj': 'what', 'kind': 'lead up', 'obj': 'stab'}},
{'event': {'subj': 'investigator', 'kind': 'work', 'event_mod': 'still', 'phrase_mod': 'to determine'}},
{'event': {'subj': 'stab', 'passive': True, 'kind': 'happen'}},
{'event': {'subj': 'altercation', 'kind': 'occur', 'sub_ord': 'when stab happen'}},
{'event': {'subj': 'they', 'kind': 'say', 'event_mod': 'however'}},
{'object': {'kind': 'motive', 'phrase_mod': 'for stab'}},
{'object': {'kind': 'dispute', 'obj_mod': 'ongoing', 'phrase_mod': 'between suspect and victim'}},
{'event': {'subj': 'motive', 'passive': True, 'kind': 'connect', 'phrase_mod': 'to dispute'}},
{'event': {'subj': 'police', 'obj': 'motive', 'kind': 'believe'}},
{'object': {'kind': 'knife', 'count': 'one'}},
{'event': {'subj': 'knife', 'passive': True, 'kind': 'use', 'phrase_mod': 'in stab'}},
{'event': {'subj': 'knife', 'passive': True, 'kind': 'seize'}},
{'person': {'kind': 'anyone', 'phrase_mod': 'with information'}},
{'event': {'kind': 'contact', 'obj': 'authorities'}},
{'event': {'subj': 'anyone', 'passive': True, 'kind': 'asked', 'phrase_mod': 'to contact'}}
]

article_3 = """
A Chinese tourist had been sentenced to 10 years in prison over the shooting death of an Egyptian soldier during a nightclub brawl in Gaza.

The shooting took place during a fight between one Egyptian soldier and two Chinese tourists at this nightclub.

The soldier was described as about 38 years old, wearing a salmon-colored jacket with a black collar and cuffs, with blue jeans and heavy shoes. The first tourist was described as about 45 years old, wearing a straight jacket with a Chinese collar and cuffs, with blue jeans and red shoes. The second tourist was described as about 48 years old, wearing a red jacket with a blue collar and cuffs, with blue jeans and flat shoes.

Nancy Grace, 38 years old, was shot to death after a fight broke out in a nightclub in the expensive resort last September.

The victim's attorney said on Friday "my client did not do anything to bring about the trouble and was attacked by two people shooting at him at the nightclub."

"This has broken me, not just my spirit, not just my family, but also my mind.", the victim's mom said, her voice trembling.

"The facts and circumstances that led up to this shooting are still being determined.", police said. "Unfortunately, we had shootings that occurred inside and outside the structure", the police told CNN on Monday. "We are trying to piece everything together." Police are asking for the cooperation of the public to come forward and help us with the investigation. The police chief earlier called the incident heartbreaking. Investigators are collecting evidence from the crime scene, officials said.

"As many as 10 rounds were fired inside, prompting some people to jump out the windows.", the news release said.

"It was scary. We were just trying to get to safety," a witness said.

Investigators are still working to determine what led up to the shooting. They, however, said some altercation occurred when gunshots were fired. Police believe the motive for the shooting is connected to an ongoing dispute between the suspect and the victim. One handgun has been seized that was used in the shooting.

Anyone with information was asked to contact the authorities.
"""

fact_table_3 = [
{'person': {'kind': 'tourist', 'nationality': 'Chinese'}},
{'object': {'kind': 'years', 'count': '10', 'place': 'prison'}},
{'person': {'kind': 'soldier', 'nationality': 'Egyptian'}},
{'object': {'kind': 'death', 'obj_mod': 'shooting', 'phrase_mod': 'of soldier'}},
{'object': {'kind': 'brawl', 'obj_mod': 'nightclub', 'location': 'Gaza'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'sentence', 'phrase_mod': ['to years', 'over death', 'during brawl']}},
{'person': {'kind': 'soldier', 'nationality': 'Egyptian', 'count': 'one'}},
{'person': {'kind': 'tourist', 'nationality': 'Chinese', 'count': 'two'}},
{'object': {'kind': 'fight', 'place': 'nightclub', 'phrase_mod': 'between soldier and tourist'}},
{'event': {'subj': 'shooting', 'kind': 'take', 'obj': 'place', 'phrase_mod': 'during fight'}},
{'object': {'kind': 'collar', 'obj_mod': 'black'}},
{'object': {'kind': 'jacket', 'obj_mod': 'salmon-colored', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'blue'}},
{'object': {'kind': 'shoes', 'obj_mod': 'heavy'}},
{'event': {'subj': 'soldier', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'soldier', 'age': '38 years old'}},
{'event': {'subj': 'soldier', 'passive': True, 'kind': 'describe'}},
{'object': {'kind': 'collar', 'obj_mod': 'Chinese'}},
{'object': {'kind': 'jacket', 'obj_mod': 'straight', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'blue'}},
{'object': {'kind': 'shoes', 'obj_mod': 'red'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'first', 'age': '45 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'object': {'kind': 'collar', 'obj_mod': 'blue'}},
{'object': {'kind': 'jacket', 'obj_mod': 'red', 'phrase_mod': 'with collar and cuff'}},
{'object': {'kind': 'jean', 'obj_mod': 'blue'}},
{'object': {'kind': 'shoes', 'obj_mod': 'flat'}},
{'event': {'subj': 'tourist', 'obj': 'jacket', 'kind': 'wear', 'phrase_mod': 'with jean and shoes'}},
{'person': {'kind': 'tourist', 'ordinal': 'second', 'age': '48 years old'}},
{'event': {'subj': 'tourist', 'passive': True, 'kind': 'describe'}},
{'person': {'kind': 'Nancy Grace', 'age': '38 years old'}},
{'object': {'kind': 'resort', 'obj_mod': 'expensive'}},
{'object': {'kind': 'nightclub', 'place': 'resort'}},
{'object': {'kind': 'September', 'obj_mod': 'last'}},
{'event': {'subj': 'fight', 'kind': 'break out', 'place': 'nightclub', 'month': 'September'}},
{'event': {'subj': 'Nancy Grace', 'passive': True, 'kind': 'shoot', 'phrase_mod': 'to death', 'sub_ord': 'after fight break out'}},
{'person': {'kind': 'attorney', 'obj_pos': 'victim'}},
{'event': {'kind': 'bring', 'phrase_mod': 'about trouble'}},
{'object': {'kind': 'anything', 'phrase_mod': 'to bring'}},
{'event': {'subj': 'client', 'neg': True, 'kind': 'do', 'obj': 'anything'}},
{'event': {'subj': 'people', 'obj': 'him', 'kind': 'shoot', 'location': 'nightclub'}},
{'person': {'kind': 'people', 'count': 'two'}},
{'event': {'subj': 'client', 'passive': True, 'kind': 'attack', 'obj': 'people'}},
{'event': {'subj': 'attorney', 'obj': 'client', 'kind': 'say', 'day': 'Friday'}},
{'event': {'subj': 'voice', 'kind': 'tremble'}},
{'event': {'subj': 'mom', 'kind': 'say'}},
{'event': {'subj': 'fact and circumstances', 'passive': True, 'kind': 'determine', 'event_mod': 'still'}},
{'event': {'subj': 'police', 'obj': 'fact and circumstances', 'kind': 'say'}},
{'event': {'subj': 'shooting', 'kind': 'occur', 'phrase_mod': ['inside structure', 'outside structure']}},
{'event': {'subj': 'we', 'obj': 'shooting', 'kind': 'have'}},
{'event': {'subj': 'police', 'obj': 'CNN', 'kind': 'tell', 'day': 'Monday', 'sub_ord': 'that we have'}},
{'event': {'kind': 'piece', 'obj': 'everything', 'event_mod': 'together'}},
{'event': {'subj': 'we', 'kind': 'try', 'phrase_mod': 'to piece'}},
{'object': {'kind': 'cooperation', 'phrase_mod': 'of public'}},
{'event': {'kind': 'come', 'event_mod': 'forward'}},
{'event': {'kind': 'help', 'obj': 'us', 'phrase_mod': 'with investigation'}},
{'event': {'subj': 'police', 'kind': 'ask', 'phrase_mod_1': 'for cooperation', 'phrase_mod_2': 'to come and help'}},
{'person': {'kind': 'chief', 'obj_mod': 'police'}},
{'object': {'kind': 'incident', 'obj_mod': 'heartbreaking'}},
{'event': {'subj': 'chief', 'obj': 'incident', 'kind': 'call'}},
{'object': {'kind': 'scene', 'obj_mod': 'crime'}},
{'object': {'kind': 'evidence', 'phrase_mod': 'from scene'}},
{'event': {'subj': 'investigator', 'obj': 'evidence', 'kind': 'collect'}},
{'event': {'subj': 'official', 'obj': 'investigator', 'kind': 'say'}},
{'object': {'kind': '10', 'obj_mod': 'as many as'}},
{'object': {'kind': 'round', 'count': '10'}},
{'person': {'kind': 'people', 'count': 'some'}},
{'event': {'kind': 'jump out', 'obj': 'windows'}},
{'event': {'subj': 'round', 'kind': 'prompt', 'obj': 'people', 'phrase_mod': 'to jump out'}},
{'event': {'subj': 'round', 'passive': True, 'kind': 'fire', 'event_mod': 'inside'}},
{'event': {'subj': 'news release', 'obj': 'round', 'kind': 'say'}},
{'event': {'subj': 'witness', 'kind': 'say'}},
{'event': {'subj': 'what', 'kind': 'lead up', 'obj': 'shooting'}},
{'event': {'subj': 'investigator', 'kind': 'work', 'event_mod': 'still', 'phrase_mod': 'to determine'}},
{'event': {'subj': 'gunshot', 'passive': True, 'kind': 'fire'}},
{'event': {'subj': 'altercation', 'kind': 'occur', 'sub_ord': 'when gunshot fire'}},
{'event': {'subj': 'they', 'kind': 'say', 'event_mod': 'however'}},
{'object': {'kind': 'motive', 'phrase_mod': 'for shooting'}},
{'object': {'kind': 'dispute', 'obj_mod': 'ongoing', 'phrase_mod': 'between suspect and victim'}},
{'event': {'subj': 'motive', 'passive': True, 'kind': 'connect', 'phrase_mod': 'to dispute'}},
{'event': {'subj': 'police', 'obj': 'motive', 'kind': 'believe'}},
{'object': {'kind': 'handgun', 'count': 'one'}},
{'event': {'subj': 'handgun', 'passive': True, 'kind': 'use', 'phrase_mod': 'in shooting'}},
{'event': {'subj': 'handgun', 'passive': True, 'kind': 'seize'}},
{'person': {'kind': 'anyone', 'phrase_mod': 'with information'}},
{'event': {'kind': 'contact', 'obj': 'authorities'}},
{'event': {'subj': 'anyone', 'passive': True, 'kind': 'asked', 'phrase_mod': 'to contact'}}
]

all_articles = [article_3]
all_fact_tables = [fact_table_3]

pega_1 = 'Police are searching for an Israeli tourist in connection with the fatal shooting of a French soldier at a nightclub in Miami on Sunday night.'
bart_1 = 'Shooting took place during a fight between one French soldier and two Israeli tourists at this nightclub. Police believe the motive for the shooting is connected to an ongoing dispute between the suspect and the victim.'
t5_1 = 'Police are investigating the shooting death of a French soldier in the U.S.'

pega_2 = 'A British tourist had been sentenced to 10 years in prison over the stabbing death of a Chinese soldier during a nightclub brawl in America. A British tourist had been sentenced to 10 years in prison over the stabbing death of a Chinese soldier during a nightclub brawl in America.'
bart_2 = 'Sanjay Gupta, 33 years old, was stabbed to death after a fight broke out in a nightclub in the expensive resort last September. Police believe the motive for the stab is connected to an ongoing dispute between the suspect and the victim. One knife has been seized that was used in the stab.'
t5_2 = 'A British tourist has been sentenced to 10 years in prison over the stabbing death of a Chinese soldier at a nightclub in America.'

pega_3 = 'Police in the US state of Florida are searching for a gunman who shot and killed a woman at a nightclub in the resort town of Turks and Caicos.'
bart_3 = 'Nancy Grace, 38 years old, was shot to death after a fight broke out in a nightclub in the expensive resort last September. Police believe the motive for the shooting is connected to an ongoing dispute between the suspect and the victim. One handgun has been seized that was used in the shooting.'
t5_3 = 'A Chinese tourist has been sentenced to 10 years in prison over the shooting death of a soldier at a nightclub in Gaza.'

summaries = [t5_3]
# 'threshold for word sense disambiguation to check \
#                               if an attribute/object is appeared as a verb/noun in a fact in the output summary.'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process config files.')

    parser.add_argument('--config_file', default='config.json',
                        help="path to a main config file")

    parser.add_argument('--eval_config_file', default='./evaluation/evaluation_config.json',
                        help="path to a evaluation config file")

    args = parser.parse_args()

    cfg_path = args.config_file
    eval_cfg_path = args.eval_config_file

    fr = open(cfg_path, 'r')
    fr_eval = open(eval_cfg_path, 'r')

    configs = json.load(fr)
    eval_configs = json.load(fr_eval)

    model_name = configs['model_name']
    fine_tuned_data = configs['fine_tuned_data']

    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en_core_web_lg')

    print('Generating articles ...')
    # num_articles = 1
    # all_articles, all_fact_tables = generate_facts(num_articles, print_generated_file=True)

    # print()
    # print('Loading a summarizer ...')
    # summaries = summarize(model_name, fine_tuned_data, all_articles)
    # print(f'Summaries: {summaries}')
    # print()

    # summaries = ['A tourist and a boy were stabbed to death in a bar']
    # all_articles = ['Two soldiers stabbed a tourist and a girl in a bar. The tourist and a girl were stabbed to death.']
    # all_fact_tables = [[{'person': {'kind': 'soldier', 'count': 'Two'}}, {'event': {'kind': 'stab', 'subj': 'soldier', 'obj': 'tourist and girl', 'location': 'bar'}}, {'event': {'kind': 'stab', 'passive': True, 'subj': 'tourist and girl', 'event_mod': 'to death'}}]]

    start_time = time.time()
    print('Measuring score ...')
    for summary, article, table in zip(summaries, all_articles, all_fact_tables):
        measure_overall_quality_score(summary, article, table, nlp, eval_configs)
    print()
    print(f'Time it took to measure quality of a summarizer: {time.time() - start_time}s')

    fr.close()
    fr_eval.close()
