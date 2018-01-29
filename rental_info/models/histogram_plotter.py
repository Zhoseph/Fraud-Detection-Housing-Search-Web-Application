import pandas
import numpy as np
import matplotlib.pyplot as plt
from metadata import attribute_names
from datetime import datetime as dt

TRAIN_FEATURE_FILE_NAME = '../data/results/normalized_features.csv'
feature_names = attribute_names.FEATURE_NAMES
raw_features_data_frame = pandas.read_csv(TRAIN_FEATURE_FILE_NAME, names=feature_names)


def plot_feature_histogram(attr_name, title, x_label, y_label, fig_name):
    fig = plt.figure()
    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    col = raw_features_data_frame.loc[:, attr_name]
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    n, bins, patches = plt.hist(col)
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts))


def plot_word_frequencies(file_name, num, fig_name, title):
    fig = plt.figure()
    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    attr = attribute_names.WORD_FREQUENCY
    data_frame = pandas.read_csv(file_name, names=attr)
    words = data_frame.loc[0:num, attr[0]]
    y_pos = np.arange(len(words))
    frequencies = data_frame.loc[0:num, attr[1]]
    plt.bar(y_pos, frequencies, align='center', alpha=0.5)
    plt.xticks(y_pos, words)
    plt.xticks(rotation=90)
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.title('Top %d %s' % (num, title))
    plt.grid(True)
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


def plot_histogram(data, title, x_label, y_label, fig_name, isGrid=False, isNormed=False):
    fig = plt.figure()
    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    n, bins, patches = plt.hist(data, normed=isNormed)
    plt.grid(isGrid)
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


def plot_pie_chart(sizes, title, fig_name):
    fig = plt.figure()
    labels = 'Outlier', 'Inlier'
    colors = ['gold', 'lightskyblue']
    explode = (0.1, 0)

    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title(title)

    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


def plot_bar_chart(sizes, fig_name):
    fig = plt.figure()
    classes = ('Outlier', 'Inlier')
    y_pos = np.arange(len(classes))

    plt.bar(y_pos, sizes, align='center', alpha=0.5)
    plt.xticks(y_pos, classes)
    plt.ylabel('Samples')
    plt.title('Number of Outliers vs. Inliers ')

    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


def plot_general_bar_chart(classes, sizes, title, labelx, labely, fig_name):
    fig = plt.figure()
    y_pos = np.arange(len(classes))
    plt.bar(y_pos, sizes, align='center', alpha=0.5)
    plt.xticks(y_pos, classes)
    plt.xlabel(labelx)
    plt.ylabel(labely)
    plt.xticks(rotation=90)
    plt.title(title)

    ts = dt.now().strftime('%Y%m%d-%H%M%S')  # Use timestamp as file id
    plt.savefig('../data/diagrams/%s_%s.png' % (fig_name, ts), bbox_inches='tight')


# plot_word_frequencies('../data/results/common_neg_2.csv', 20, 'neg_word_freq', 'negative words')

# FEATURE_NAMES = ['grammatical_error',
#                  'punctuation_mark',
#                  'uppercase_letter',
#                  'passive_sentence',
#                  'positive_sentiment',
#                  'negative_sentiment',
#                  'positive_emotion',
#                  'negative_emotion',
#                  'modal_verb',
#                  'strong_modal',
#                  'weak_modal',
#                  'avg_word_length',
#                  'avg_sentence_length',
#                  'log_word_count',
#                  'fog_index',
#                  'emotiveness']
# plot_feature_histogram(feature_names[0], 'Histogram of Grammatical Errors', 'Errors', 'Samples', 'grammar')
# plot_feature_histogram(feature_names[1], 'Histogram of Punctuation Ratio', 'Ratio', 'Samples', 'punctuation')
# plot_feature_histogram(feature_names[2], 'Histogram of Uppercase Letter Ratio', 'Ratio', 'Samples', 'uppercase')
# plot_feature_histogram(feature_names[3], 'Histogram of Passive Sentences Ratio', 'Ratio', 'Samples', 'passive')
# plot_feature_histogram(feature_names[4], 'Histogram of Positive Words Ratio', 'Ratio', 'Samples', 'pos_words')
# plot_feature_histogram(feature_names[5], 'Histogram of Negative Words Ratio', 'Ratio', 'Samples', 'neg_words')
# plot_feature_histogram(feature_names[6], 'Histogram of Positive Emotion Words Ratio', 'Ratio', 'Samples',
#                        'pos_emotion_words')
# plot_feature_histogram(feature_names[7], 'Histogram of Negative Emotion Words Ratio', 'Ratio', 'Samples',
#                        'neg_emotion_words')
# plot_feature_histogram(feature_names[8], 'Histogram of Modal Verbs Ratio', 'Ratio', 'Samples', 'modal_verbs')
# plot_feature_histogram(feature_names[9], 'Histogram of Strong Modals Ratio', 'Ratio', 'Samples', 'strong_modals')
# plot_feature_histogram(feature_names[10], 'Histogram of Weak Modals Ratio', 'Ratio', 'Samples', 'weak_modals')
# plot_feature_histogram(feature_names[11], 'Histogram of Average Word Length', 'Average', 'Samples', 'avg_word_length')
# plot_feature_histogram(feature_names[12], 'Histogram of Average Sentence Length', 'Average', 'Samples',
#                        'avg_sentence_length')
# plot_feature_histogram(feature_names[13], 'Histogram of Log of Word Count', 'Log', 'Samples', 'log_word_count')
# plot_feature_histogram(feature_names[14], 'Histogram of Fog Index', 'Fog Index', 'Samples', 'fog_index')
# plot_feature_histogram(feature_names[15], 'Histogram of Emotiveness', 'Emotiveness', 'Samples', 'emotiveness')
# plot_word_frequencies('../data/results/common_pos_ALL.csv', 20, 'frequency_positive_words', 'Positive Words')
# plot_word_frequencies('../data/results/common_neg_ALL.csv', 20, 'frequency_negative_words', 'Negative Words')
