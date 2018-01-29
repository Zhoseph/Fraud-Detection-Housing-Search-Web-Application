from aenum import Enum
import json
import csv


class Tag(Enum):
    def __str__(self):
        return str(self.value)
    negative = 0
    positive = 1
    strong = 2
    weak = 3


def write_to_csv(path, data):
    with open(path, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


def file_to_dict(file_name, tag, splitter=None):
    d = {}
    with open(file_name) as f:
        if splitter is None:
            for line in f:
                d[line.strip().lower()] = tag
        else:
            for line in f:
                word_list = line.split(splitter)
                for w in word_list:
                    d[w.strip().lower()] = tag
    return d


def file_to_set(file_name, splitter=None):
    s = set()
    with open(file_name) as f:
        if splitter is None:
            for line in f:
               s.add(line.strip().lower())
        else:
            for line in f:
                word_list = line.split(splitter)
                for w in word_list:
                    s.add(line.strip().lower())
    return s


def file_to_json(file_name):
    with open(file_name) as data_file:
        data = json.load(data_file)
        return data;


def write_to_file(file_name, col_names, sorted_list, top_n=1000):
    with open(file_name, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        i = 0
        while i < len(sorted_list) and i < top_n:
            pos_tup = sorted_list[i]
            i += 1
            writer.writerow([pos_tup[0], pos_tup[1]])


# my_dict = file_to_dict('../data/sentiment_analysis/positive.txt', Tag.positive)
# print str(my_dict['excellent'])
#
# emotion_dict = file_to_dict('../data/words/positive_emotion_words.txt', Tag.positive, ',')
# print str(my_dict['excellent'])
