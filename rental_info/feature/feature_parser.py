from utilities import file_parser as fp
from utilities import text_analyzer as ta
from bs4 import BeautifulSoup
import csv
from time import time
import feature_selector as feature_selector
import utilities.passive_detector as pd
from metadata import attribute_names

# Log (the number of words in the document)
# Fog Index = (average sentence length + (the number of words with 3  syllables or more / total number of words)) * 0.4
# Emotiveness = Total number of adjectives and adverbs / total number of nouns and verbs

STAT_PRINT_POINT = 200
FEATURES_FILE_NAME = "test_features.csv"
CORPUS_NAME = "../data/datasets/test.json"

with open(FEATURES_FILE_NAME, "ab") as f:
    writer = csv.writer(f)
    writer.writerow(attribute_names.FEATURE_NAMES)

    json_data = fp.file_to_json(CORPUS_NAME)
    all_descriptions = json_data['description']
    counter = 0
    skipped = 0
    feature_list = []
    print('Extracting features from corpus %s to destination file %s' % (CORPUS_NAME, FEATURES_FILE_NAME))
    t0 = time()

    for id, desc in all_descriptions.iteritems():
        counter += 1

        # print '--- ID:\t' + str(id) + '\t--- Iteration:\t' + str(counter)
        soup = BeautifulSoup(desc, 'lxml')
        document = soup.get_text()
        # print document

        fs = feature_selector.FeatureSelector(document, ta.ARTICLE_SET)
        # skip if word count of the description is zero
        if fs.get_word_count() == 0:
            skipped += 1
            print '*** SK:\t' + str(id) + '\t--- Number:\t' + str(skipped)
            continue

        f1 = fs.count_grammatical_errors()
        f2 = fs.calculate_punctuation_ratio()
        f3 = fs.calculate_uppercase_letter_ratio()

        f4 = fs.calculate_passive_sentence_ratio(pd.TAGGER)
        f5 = fs.calculate_word_ratio(feature_selector.POSITIVE_WORDS)
        f6 = fs.calculate_word_ratio(feature_selector.NEGATIVE_WORDS)

        # positive emotion words
        positive_emotion_1 = fs.calculate_word_ratio(feature_selector.POSITIVE_EMOTION_WORDS)
        positive_emotion_2 = fs.calculate_ngram_word_ratio(2, feature_selector.POSITIVE_EMOTION_WORDS)
        positive_emotion_3 = fs.calculate_ngram_word_ratio(3, feature_selector.POSITIVE_EMOTION_WORDS)
        positive_emotion_4 = fs.calculate_ngram_word_ratio(4, feature_selector.POSITIVE_EMOTION_WORDS)
        f7 = positive_emotion_1 + positive_emotion_2 + positive_emotion_3 + positive_emotion_4

        # negative emotion words
        negative_emotion_1 = fs.calculate_word_ratio(feature_selector.NEGATIVE_EMOTION_WORDS)
        negative_emotion_2 = fs.calculate_ngram_word_ratio(2, feature_selector.NEGATIVE_EMOTION_WORDS)
        negative_emotion_3 = fs.calculate_ngram_word_ratio(3, feature_selector.NEGATIVE_EMOTION_WORDS)
        negative_emotion_4 = fs.calculate_ngram_word_ratio(4, feature_selector.NEGATIVE_EMOTION_WORDS)
        f8 = negative_emotion_1 + negative_emotion_2 + negative_emotion_3 + negative_emotion_4

        f9 = fs.calculate_verb_ratio(feature_selector.MODAL_VERBS)
        f10 = fs.calculate_verb_ratio(feature_selector.STRONG_MODAL_WORDS)
        f11 = fs.calculate_verb_ratio(feature_selector.WEAK_MODAL_WORDS)

        f12 = fs.calculate_average_word_length()
        f13 = fs.calculate_average_sentence_length()
        f14 = fs.calculate_log_document_length()

        f15 = fs.calculate_fog_index()
        f16 = fs.calculate_emotiveness()
        feature_list = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16]
        writer.writerow(feature_list)

        if counter % STAT_PRINT_POINT == 0:
            print '--- ID:\t' + str(id) + '\t--- Iteration:\t' + str(counter)
            print 'Total number of records: %d' % counter
            print 'Total number of skipped records: %d' % skipped
            print 'Done in %.3f minutes' % ((time() - t0) / 60)

    duration = time() - t0
    print 'Extracted features from corpus %s to destination file %s' % (CORPUS_NAME, FEATURES_FILE_NAME)
    print 'Total number of features: %d' % len(feature_list)
    print 'Total number of records: %d' % counter
    print 'Total number of skipped records: %d' % skipped
    print 'Done in %.3f minutes' % (duration / 60)
