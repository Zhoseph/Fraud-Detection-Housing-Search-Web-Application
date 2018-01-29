from nltk import word_tokenize
from nltk import ne_chunk
from nltk.tag import pos_tag, map_tag
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import sent_tokenize
from nltk.corpus import cmudict
from nltk import ngrams
from commonregex import CommonRegex
from aenum import Enum
from nameparser.parser import HumanName
from gensim import corpora, models
from collections import Counter
from contraction import CONTRACTION_MAP
import logging
import string
import enchant
import file_parser as fp


class Information(Enum):
    address = 1
    email = 2
    link = 3
    phone = 4
    price = 5
    date = 6
    time = 7


class Pos(Enum):
    verb = 1
    noun = 2
    adjective = 3
    adverb = 4
    modal = 5


# names
ALL_NAMES = fp.file_to_set('../data/words/all_names.txt')
# used for when counting total number of words
ARTICLE_SET = {'a', 'an', 'the'}
STOP_WORDS = set(stopwords.words('english'))
IGNORE_CHARACTERS = {' ', '\n', '\t', '\r', '-', '_'}

cmu_dict = cmudict.dict()

# https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
# https://datascience.stackexchange.com/questions/5639/fraud-detection-use-text-mining

logging.basicConfig(filename='../logs/fraud.log',
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)
# Suppress info messages from the 'gensim' library
logging.getLogger('gensim').setLevel(logging.INFO)


def count_words(document, stop_words, to_lower):
    list_of_words = cleanup_text(document, stop_words, to_lower)
    if list_of_words is None:
        return 0
    return len(list_of_words)


def count_sentences(document):
    sentence_list = sent_tokenize(document)
    if sentence_list is None:
        return 0
    return len(sentence_list)


def get_sentences(document):
    return sent_tokenize(document)


def count_syllables(word):
    # https://stackoverflow.com/questions/5087493/to-find-the-number-of-syllables-in-a-word
    # returns a list of numbers
    pronunciation_list = cmu_dict.get(word.lower())
    if pronunciation_list is None or len(pronunciation_list) < 1:
        return []
    return [len(list(y for y in x if str(y[-1]).isdigit())) for x in pronunciation_list]


def count_uppercase_letters(text):
    return sum(1 for c in text if c.isupper())


def count_characters(word):
    return len([c for c in word if c not in IGNORE_CHARACTERS])


def count_punctuations(text):
    counts = Counter(text)
    punctuation_counts_dict = {k: v for k, v in counts.iteritems() if k in string.punctuation}
    return punctuation_counts_dict, sum(punctuation_counts_dict.values())


def is_complex_word(w):
    syllables_list = count_syllables(w)
    if syllables_list is None or len(syllables_list) < 1:
        return False
    # if word has more than 2 syllables
    return syllables_list[0] > 2


def count_pos_tags(text, tag_set):
    tagged = get_pos_tags(text)
    counts = Counter(tag for word, tag in tagged)
    result = {}
    if Pos.verb in tag_set:
        result[Pos.verb] = counts['VB'] + \
                           counts['VBD'] + \
                           counts['VBN'] + \
                           counts['VBD'] + \
                           counts['VBZ']
    if Pos.noun in tag_set:
        result[Pos.noun] = counts['NN'] + \
                           counts['NNS'] + \
                           counts['NNP'] + \
                           counts['NNPS']
    if Pos.adjective in tag_set:
        result[Pos.adjective] = counts['JJ'] + \
                                counts['JR'] + \
                                counts['JRS']
    if Pos.adverb in tag_set:
        result[Pos.adverb] = counts['RB'] + \
                             counts['RBR'] + \
                             counts['RBS']
    if Pos.modal in tag_set:
        result[Pos.modal] = counts['MD']
    return result


def expand_contraction(document):
    if document is None:
        logging.info('No sentence to parse')
        return []
    words = document.split()
    processed_list = []
    for w in words:
        lowered_word = w.lower()
        if lowered_word in CONTRACTION_MAP:
            processed_list.append(CONTRACTION_MAP[lowered_word])
        else:
            processed_list.append(w)
    return ' '.join(processed_list)


def cleanup_text(document, stop_words, to_lower=True):
    if document is None:
        logging.info('No sentence to parse')
        return
    processed_text = expand_contraction(document)
    if to_lower:
        processed_text = processed_text.lower()
    # 1. tokenize
    tokens = word_tokenize(processed_text)
    # 2. remove stop words and punctuations
    cleaned = []
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    for token in tokens:
        if token is None or token == '':
            continue
        if token not in stop_words and not is_link(token):
            # 3. remove punctuations
            token = token.translate(remove_punctuation_map)
            if not token == '':
                cleaned.append(token)
    return cleaned


def create_ngram_phrases(sentence, n):
    if sentence is None:
        return []
    grams_list = []
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    grams = get_ngrams(sentence, n)
    for tup in grams:
        phrase = ''
        for m in tup:
            no_punc = m.translate(remove_punctuation_map)
            phrase = phrase + no_punc + ' '
        grams_list.append(phrase.rstrip().lower())
    return grams_list


def correct_spelling(tokens):
    corrected = []
    if tokens is None:
        logging.info('No tokens to spell check')
        return {}
    d = enchant.Dict("en_US")
    grammatical_errors = {}
    for t in tokens:
        if t is None or t == '':
            continue
        if t in CONTRACTION_MAP or t in ALL_NAMES or is_link(t):
            continue
        if d.check(t):
            corrected.append(t)
        else:
            suggestions = d.suggest(t)
            if len(suggestions) > 0:
                grammatical_errors[t] = suggestions
                # get the most likely corrected token from the list
                corrected.append(suggestions[0])
    # len(grammatical_errors) gives the total number of grammatical errors
    return corrected, grammatical_errors


def extract_stem(tokens):
    stems = []
    # Create an instance of class PorterStemmer
    p_stemmer = PorterStemmer()
    for t in tokens:
        if t is None or t == '':
            continue
        stems.append(p_stemmer.stem(t))
    return stems


def get_pos_tags(cleaned_tokens, check_spelling=True):
    if check_spelling:
        # correct spelling errors
        corrected_tokens, errors = correct_spelling(cleaned_tokens)
        return pos_tag(corrected_tokens)
    else:
        return pos_tag(cleaned_tokens)


def get_simplified_pos_tags(pos_tagged):
    # get simplified tags
    simplified_tags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in pos_tagged]
    return simplified_tags


def get_human_names(text):
    pos_tagged = get_pos_tags(cleanup_text(text, STOP_WORDS, False), False)
    chunked_sentences = ne_chunk(pos_tagged, binary=False)
    person_list = []
    person = []
    name = ''
    for subtree in chunked_sentences.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1:
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return person_list


def parse_name(name):
    name = HumanName(name)
    return name


# HumanName : [
#     title: 'Dr.'
#     first: 'Juan'
#     middle: 'Q. Xavier'
#     last: 'de la Vega'
#     suffix: 'III'
#     nickname: 'Doc Vega'
# ]


def find_info(text, attribute):
    if text is None:
        return []
    parsed_text = CommonRegex(text)
    if attribute == Information.link:
        return parsed_text.links
    if attribute == Information.email:
        return parsed_text.emails
    if attribute == Information.time:
        return parsed_text.times
    if attribute == Information.date:
        return parsed_text.dates
    if attribute == Information.phone:
        return parsed_text.phones
    if attribute == Information.price:
        return parsed_text.prices
    if attribute == Information.address:
        return parsed_text.street_addresses


def is_link(token):
    link_list = find_info(token, Information.link)
    if len(link_list) > 0 and link_list[0] == token:
        return True
    return False


def get_bow(texts):
    # texts is a list of lists, each list contains tokens of a document
    # Dictionary assigns a unique integer id to each unique token
    # also collecting word counts and relevant statistics
    dictionary = corpora.Dictionary(texts)
    bow = [dictionary.doc2bow(text) for text in texts]
    # bow is a list of vectors, each vector is for a document
    return bow, dictionary


def is_name(word):
    return word in ALL_NAMES


def get_ngrams(sentence, n):
    grams = ngrams(sentence.split(), n)
    return grams


def get_lda(texts):
    corpus, dictionary = get_bow(texts)
    # more passes more accurate but gets slower with large documents
    # Adjusting the number of topics and passes are important to getting a good result
    lda_model = models.ldamodel.LdaModel(corpus, num_topics=3, id2word=dictionary, passes=20)
    # print ldamodel.print_topics(num_topics=3, num_words=4)
    return lda_model


# print count_pos_tags("It has been a nice day although I've been feeling sleepy.",
#                      {Pos.verb, Pos.noun, Pos.adjective, Pos.adverb, Pos.modal})
#
# print count_uppercase_letters("test123")
# print is_complex_word('extraordinary')
# grams = get_ngrams("Hello world! how are you? We're doing great.", 3)
# for g in grams:
#     print g
# create_ngram_phrases("Hello world! how are you? We're doing great.", 3)
