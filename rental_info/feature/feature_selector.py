import utilities.text_analyzer as ta
import utilities.passive_detector as pd
import utilities.file_parser as fp
from bs4 import BeautifulSoup
from math import log
import logging

# decimal points
NUM_DIGITS = 3
# Red flag phrases
RED_FLAGS = {'free credit check'}
# sentiments
POSITIVE_WORDS = fp.file_to_set('../data/sentiment_analysis/positive.txt')
NEGATIVE_WORDS = fp.file_to_set('../data/sentiment_analysis/negative.txt')
# modals
STRONG_MODAL_WORDS = fp.file_to_set('../data/words/strong_modal_words.txt')
WEAK_MODAL_WORDS = fp.file_to_set('../data/words/weak_modal_words.txt')
MODAL_VERBS = fp.file_to_set('../data/words/modal_verbs.txt')
# emotion
# For emotion words also try with 2,3, and 4 grams
POSITIVE_EMOTION_WORDS = fp.file_to_set('../data/words/positive_emotion_words.txt')
NEGATIVE_EMOTION_WORDS = fp.file_to_set('../data/words/negative_emotion_words.txt')


class FeatureSelector(object):
    def __init__(
            self,
            document,
            stop_words=ta.ARTICLE_SET
    ):
        self.document = document
        self.stop_words = stop_words
        self.words = ta.cleanup_text(document, stop_words, True)
        self.raw_words = ta.cleanup_text(document, stop_words, False)
        self.word_count = 0 if self.words is None else len(self.words)
        self.sentences = ta.get_sentences(document)
        self.sentence_count = 0 if self.sentences is None else len(self.sentences)
        self.pos_count = ta.count_pos_tags(self.words, {ta.Pos.verb,
                                                        ta.Pos.noun,
                                                        ta.Pos.adjective,
                                                        ta.Pos.adverb,
                                                        ta.Pos.modal})

        logging.basicConfig(filename='../logs/feature_selector.log',
                            format='%(asctime)s %(message)s',
                            level=logging.DEBUG)

    def get_stopwords(self):
        return self.stop_words

    def get_document(self):
        return self.document

    def get_word_count(self):
        return self.word_count

    def get_words(self):
        return self.words

    def get_raw_words(self):
        return self.raw_words

    # Num of grammatical errors
    def count_grammatical_errors(self):
        corrected, grammatical_errors = ta.correct_spelling(self.words)
        if grammatical_errors is None:
            return 0
        return len(grammatical_errors)

    # ratio of positive words
    # ratio of negative words
    # ratio of uni-gram positive emotion words
    # ratio of uni-gram negative emotion words
    def calculate_word_ratio(self, ref_word_set):
        if self.word_count == 0 \
                or ref_word_set is None or len(ref_word_set) == 0:
            return 0
        total = 0
        for w in self.words:
            if w in ref_word_set:
                total += 1
        ratio = total / float(self.word_count)
        return round(ratio, NUM_DIGITS)

    # to check more than 1 grams
    def calculate_ngram_word_ratio(self, n, ref_word_set):
        if self.word_count == 0:
            return 0
        if n < 2 or self.sentences is None or \
                        ref_word_set is None or len(ref_word_set) == 0:
            return []
        total = 0
        for s in self.sentences:
            grams_list = ta.create_ngram_phrases(s, n)
            if grams_list is None:
                continue
            for gram in grams_list:
                if gram in ref_word_set:
                    total += 1
        ratio = total / float(self.word_count)
        return round(ratio, NUM_DIGITS)

    # ratio of modal verbs
    # ratio of strong modal words
    # ratio of weak modal words
    def calculate_verb_ratio(self, ref_word_set):
        if self.word_count == 0 or self.pos_count is None \
                or ref_word_set is None or len(ref_word_set) == 0:
            return 0
        total = 0
        for w in self.words:
            if w in ref_word_set:
                total += 1
        if self.pos_count[ta.Pos.verb] == 0:
            return total
        ratio = total / float(self.pos_count[ta.Pos.verb])
        return round(ratio, NUM_DIGITS)

    # ratio of punctuation marks
    def calculate_punctuation_ratio(self):
        if self.sentence_count == 0:
            return 0
        punc_dict, total = ta.count_punctuations(self.document)
        if self.pos_count[ta.Pos.verb] == 0:
            return total
        ratio = total / float(self.sentence_count)
        return round(ratio, NUM_DIGITS)

    # ratio of passive sentences
    def calculate_passive_sentence_ratio(self, tagger):
        if self.sentence_count == 0:
            return 0
        total = pd.count_passive_sentences(self.document, tagger)
        ratio = total / float(self.sentence_count)
        return round(ratio, NUM_DIGITS)

    # average sentence length
    def calculate_average_sentence_length(self):
        if self.sentence_count == 0:
            return 0
        ratio = self.word_count / float(self.sentence_count)
        return round(ratio, NUM_DIGITS)

    # average word length
    def calculate_average_word_length(self):
        if self.word_count == 0:
            return 0
        total = 0
        for w in self.words:
            total += ta.count_characters(w)
        ratio = total / float(self.word_count)
        return round(ratio, NUM_DIGITS)

    # ratio of uppercase letters
    def calculate_uppercase_letter_ratio(self):
        if self.word_count == 0:
            return 0
        total = 0
        upper = 0
        for w in self.raw_words:
            total += ta.count_characters(w)
            upper += ta.count_uppercase_letters(w)
        if total == 0:
            return 0
        ratio = upper / float(total)
        return round(ratio, NUM_DIGITS)

    # logarithm of document length
    def calculate_log_document_length(self):
        # natural logarithm
        if self.word_count == 0:
            return 0
        return round(log(self.word_count), NUM_DIGITS)

    # fog index is (average sentence length + ratio of complex words) * 0.4
    def calculate_fog_index(self):
        if self.word_count == 0:
            return 0
        num_complex_words = 0
        for w in self.words:
            if ta.is_complex_word(w):
                num_complex_words += 1
        fog_index = (self.calculate_average_sentence_length() + num_complex_words / float(self.word_count)) * 0.4
        return round(fog_index, NUM_DIGITS)

    # calculate emotiveness
    def calculate_emotiveness(self):
        if self.word_count == 0 or self.pos_count is None:
            return 0
        adj_and_adv = self.pos_count[ta.Pos.adjective] + self.pos_count[ta.Pos.adverb]
        noun_and_verb = self.pos_count[ta.Pos.noun] + self.pos_count[ta.Pos.verb]
        if noun_and_verb == 0:
            return adj_and_adv
        ratio = adj_and_adv / float(noun_and_verb)
        return round(ratio, NUM_DIGITS)


def get_features(description):
    soup = BeautifulSoup(description, 'lxml')
    document = soup.get_text()

    feature_selector_obj = FeatureSelector(document, ta.ARTICLE_SET)
    f1 = feature_selector_obj.count_grammatical_errors()
    f2 = feature_selector_obj.calculate_punctuation_ratio()
    f3 = feature_selector_obj.calculate_uppercase_letter_ratio()

    f4 = feature_selector_obj.calculate_passive_sentence_ratio(pd.TAGGER)
    f5 = feature_selector_obj.calculate_word_ratio(POSITIVE_WORDS)
    f6 = feature_selector_obj.calculate_word_ratio(NEGATIVE_WORDS)

    # positive emotion words
    positive_emotion_1 = feature_selector_obj.calculate_word_ratio(POSITIVE_EMOTION_WORDS)
    positive_emotion_2 = feature_selector_obj.calculate_ngram_word_ratio(2, POSITIVE_EMOTION_WORDS)
    positive_emotion_3 = feature_selector_obj.calculate_ngram_word_ratio(3, POSITIVE_EMOTION_WORDS)
    positive_emotion_4 = feature_selector_obj.calculate_ngram_word_ratio(4, POSITIVE_EMOTION_WORDS)
    f7 = positive_emotion_1 + positive_emotion_2 + positive_emotion_3 + positive_emotion_4

    # negative emotion words
    negative_emotion_1 = feature_selector_obj.calculate_word_ratio(NEGATIVE_EMOTION_WORDS)
    negative_emotion_2 = feature_selector_obj.calculate_ngram_word_ratio(2, NEGATIVE_EMOTION_WORDS)
    negative_emotion_3 = feature_selector_obj.calculate_ngram_word_ratio(3, NEGATIVE_EMOTION_WORDS)
    negative_emotion_4 = feature_selector_obj.calculate_ngram_word_ratio(4, NEGATIVE_EMOTION_WORDS)
    f8 = negative_emotion_1 + negative_emotion_2 + negative_emotion_3 + negative_emotion_4

    f9 = feature_selector_obj.calculate_verb_ratio(MODAL_VERBS)
    f10 = feature_selector_obj.calculate_verb_ratio(STRONG_MODAL_WORDS)
    f11 = feature_selector_obj.calculate_verb_ratio(WEAK_MODAL_WORDS)

    f12 = feature_selector_obj.calculate_average_word_length()
    f13 = feature_selector_obj.calculate_average_sentence_length()
    f14 = feature_selector_obj.calculate_log_document_length()

    f15 = feature_selector_obj.calculate_fog_index()
    f16 = feature_selector_obj.calculate_emotiveness()
    feature_list = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16]
    return feature_list
