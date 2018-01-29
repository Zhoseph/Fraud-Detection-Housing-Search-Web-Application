from utilities import file_parser as fp
from time import time
from collections import defaultdict
from metadata import attribute_names
import operator


CORPUS_NAME = "../data/datasets/train.json"


json_data = fp.file_to_json(CORPUS_NAME)
all_image_lists = json_data['photos']

photo_frequency_dict = defaultdict(int)

print 'Collecting number of photos data from corpus %s ' %(CORPUS_NAME)
t0 = time()
counter = 0
for id, image_list in all_image_lists.iteritems():
    if image_list is None:
        continue
    counter += 1
    photo_frequency_dict[len(image_list)] += 1
print 'Total number of records: %d' % counter
print 'Done in %.3f minutes' % ((time() - t0) / 60)

sorted_photo_counts = sorted(photo_frequency_dict.items(), key=operator.itemgetter(0))
fp.write_to_file("../data/results/image_counts.csv", attribute_names.IMAGE_COUNT_FREQUENCY, sorted_photo_counts)

from models.histogram_plotter import plot_general_bar_chart
plot_general_bar_chart(photo_frequency_dict.keys(),
                       photo_frequency_dict.values(),
                       'Number of images in samples',
                       'Image count',
                       'Samples',
                       'image_counts')

