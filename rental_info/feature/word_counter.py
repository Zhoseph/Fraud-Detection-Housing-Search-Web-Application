from utilities import file_parser as fp
from utilities import text_analyzer as ta
from bs4 import BeautifulSoup
from time import time
from feature_selector import NEGATIVE_WORDS as neg_words
from feature_selector import POSITIVE_WORDS as pos_words
from collections import defaultdict
import operator
from metadata import attribute_names
from utilities.file_parser import write_to_file


STAT_PRINT_POINT = 1000
TOP_N_NUM = 100
COMMON_POSITIVE_FILE_NAME = "common_pos_2.csv"
COMMON_NEGATIVE_FILE_NAME = "common_neg_2.csv"
CORPUS_NAME = "../data/datasets/train.json"


json_data = fp.file_to_json(CORPUS_NAME)
all_descriptions = json_data['description']
all_image_lists = json_data['photos']
counter = 0
skipped = 0
feature_list = []
neg_word_frequency_dict = defaultdict(int)
pos_word_frequency_dict = defaultdict(int)
print('Collecting word frequencies from corpus %s to destination files %s and %s' % (CORPUS_NAME,
                                                                                     COMMON_POSITIVE_FILE_NAME,
                                                                                     COMMON_NEGATIVE_FILE_NAME))
t0 = time()

for id, desc in all_descriptions.iteritems():
    counter += 1
    # if counter > NUM_OF_RECORDS:
    #     break
    # print '\t--- ID:\t' + str(id) + '\t--- Iteration:\t' + str(counter)
    soup = BeautifulSoup(desc, 'lxml')
    document = soup.get_text()
    # print document

    words = ta.cleanup_text(document, ta.ARTICLE_SET, True)
    if words is None or len(words) == 0:
        skipped += 1
        # print '\t*** SK:' + str(id) + '\t--- Number:\t' + str(skipped)
        continue

    for w in words:
        if w in pos_words:
            pos_word_frequency_dict[w] += 1
        if w in neg_words:
            neg_word_frequency_dict[w] += 1

    if counter % STAT_PRINT_POINT == 0:
        print 'Total number of records: %d' % counter
        print 'Total number of skipped records: %d' % skipped
        print 'Done in %.3f minutes' % ((time() - t0) / 60)
        print '---------------------------------------------'

sorted_desc_neg = sorted(neg_word_frequency_dict.items(), key=operator.itemgetter(1), reverse=True)
sorted_desc_pos = sorted(pos_word_frequency_dict.items(), key=operator.itemgetter(1), reverse=True)
write_to_file(COMMON_NEGATIVE_FILE_NAME, attribute_names.WORD_FREQUENCY, sorted_desc_neg, TOP_N_NUM)
write_to_file(COMMON_POSITIVE_FILE_NAME, attribute_names.WORD_FREQUENCY, sorted_desc_pos, TOP_N_NUM)

duration = time() - t0
print 'Collecting word frequencies from corpus %s to destination files %s and %s' % (CORPUS_NAME,
                                                                    COMMON_POSITIVE_FILE_NAME,
                                                                    COMMON_NEGATIVE_FILE_NAME)
print 'Total number of features: %d' % len(feature_list)
print 'Total number of records: %d' % counter
print 'Total number of skipped records: %d' % skipped
print 'Done in %.3f minutes' % (duration / 60)

