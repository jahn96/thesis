"""
    This code uses question generation methods from Durmus et al. (2020)
"""
"""
    The metric represents the information of a source document by a set of question-answer pairs
    that are automatically generated from the source document.

    Then, QAEval estimates how much of this information is in a candidate summary
    by using a learned QA model to answer the questions against the candidate.

    The predictions from the QA model are verified as correct or incorrect,
    then the final score of the metric calculates what proportion of the questions were answered correctly.
"""
from fairseq.models.bart import BARTModel
import nltk
import spacy
import benepar
import tensorflow as tf
from nltk.corpus import stopwords
from nltk.tree import Tree
from transformers import pipeline
import numpy as np

# TODO: 1. generate question and answer pairs based on source document/table of facts
#          - Using Durmus et al. (2020)'s question generation model or grammar based generation
# TODO: 2. check if the question is answerable by a learned QA model given a candidate summary
# TODO: 3. calculate how many of the questions can be answered

class QACov:
    def __init__(self, bart_qa_dir='./evaluation/comprehensiveness/qg_model/checkpoints/', use_gpu=False):
        self.qg_model = BARTModel.from_pretrained(
            bart_qa_dir,
            checkpoint_file='checkpoint_best.pt'
        )

        if use_gpu:
            self.qg_model.cuda()
            self.qg_model.half()

        self.qg_model.eval()

        self.batch_size = 64
        self.beam_size = 10
        self.max_length = 100

        self.nlp = spacy.load('en_core_web_sm')
        self.parser = benepar.Parser("benepar_en2")
        self.stop_words = set(stopwords.words('english'))

    def _get_entities(self, output_summary):
        entities = [X.text for X in self.nlp(output_summary).ents]
        return entities

    def _get_masked_phrases(self, output_summary, phrase_types=["NP"]):
        masked_phrases = []
        parse_tree = self.parser.parse(output_summary)
        for subtree in parse_tree.subtrees():
            phrases_list = [(subtree_.leaves(), subtree_.label()) for subtree_ in subtree if
                            type(subtree_) == Tree and subtree_.label() in phrase_types]
            for phrase_tuple in phrases_list:
                phrase = phrase_tuple[0]
                phrase_type = phrase_tuple[1]
                phrase_text = " ".join(phrase)
                if len(phrase) > 0 and phrase_text not in self.stop_words:
                    masked_phrases.append(phrase_text)

        return masked_phrases

    # TODO: Too expensive... just use grammar to formulate questions ?
    def _generate_questions(self, facts, entities=True, phrase_types=["NP"]):
        doc_ids = []
        qa_masks = []
        tokenized_phrases = []

        for id_, fact in enumerate(facts):
            fact = fact.strip()
            all_masked_phrases = []
            if entities:
                all_masked_phrases.extend(self._get_entities(fact))
            all_masked_phrases.extend(self._get_masked_phrases(fact, phrase_types))
            all_masked_phrases = list(set(all_masked_phrases))

            for i, masked_phrase in enumerate(all_masked_phrases):
                tokenized_summary = " ".join(nltk.word_tokenize(fact.lower()))
                tokenized_phrase = " ".join(nltk.word_tokenize(masked_phrase.lower()))

                qa_masks.append(tokenized_summary + " [SEP] " + tokenized_phrase)
                doc_ids.append(str(id_))
                tokenized_phrases.append(tokenized_phrase)

        questions = []
        for i in range(0, len(qa_masks), self.batch_size):
            batch = qa_masks[i:i + self.batch_size]
            hypotheses = self.qg_model.sample(batch, beam=self.beam_size, lenpen=1.0, max_len_b=self.max_length,
                                              min_len=1, no_repeat_ngram_size=3)
            questions.extend(hypotheses)

        return doc_ids, questions, tokenized_phrases

    def _run_squad(self, questions, context):
        model_name = "deepset/roberta-base-squad2"

        # a) Get predictions
        nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

        outputs = []
        candidate_answers = []
        for question in questions:
            QA_input = {
                'question': question,
                'context': context
            }
            res = nlp(QA_input)
            outputs.append(res)
            candidate_answers.append(res['answer'])
        return outputs, candidate_answers

    def _compute_f1(self, gold_answer, candidate_answer):
        gold_answer_doc = self.nlp(gold_answer)
        candidate_answer_doc = self.nlp(candidate_answer)

        # remove stopwords
        gold_toks = [gold_tok.text for gold_tok in gold_answer_doc if not gold_tok.is_stop]
        candidate_toks = [cand_tok.text for cand_tok in candidate_answer_doc if not cand_tok.is_stop]

        # TODO: instead of measuring pure intersection, we consider similarity?
        num_common = len(set(gold_toks).intersection(set(candidate_toks)))

        if not num_common or not len(gold_toks) or not len(candidate_toks):
            return 0

        precision = num_common / len(candidate_toks)
        recall = num_common / len(gold_toks)

        f1 = 2 * precision * recall / (precision + recall)

        return f1

    def compute_score(self, summary, source_doc):
        facts = nltk.sent_tokenize(source_doc.strip())
        doc_ids, questions, tokenized_phrases = self._generate_questions(facts)
        squad_out, candidate_answers = self._run_squad(questions, summary)

        print(questions)
        print(tokenized_phrases)
        print(candidate_answers)

        score = np.mean([self._compute_f1(gold_answer, candidate_answer) for gold_answer, candidate_answer in
                        zip(tokenized_phrases, candidate_answers)])
        return score


if __name__ == '__main__':
    tf.get_logger().setLevel('ERROR')

    qaCov = QACov()

    context = "The cue ball is green. The tennis balls are yellow. The ping pong ball is orange."
    summary = "The tennis balls are yellow and the ping pong balls are orange. The cue ball is green. The tennis balls have different colours for each match."
    f1 = qaCov.compute_score(summary, context)
    print(f1)
