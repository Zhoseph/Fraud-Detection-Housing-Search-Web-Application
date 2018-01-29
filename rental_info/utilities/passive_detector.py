from nltk import word_tokenize, tokenize
from itertools import dropwhile
from tagging import pos_tagger


# reference: https://github.com/j-c-h-e-n-g/nltk-passive-voice
TAGGER = pos_tagger.get_tagger()

def tag_sentence(sent, tagger):
    """Take a sentence as a string and return a list of (word, tag) tuples."""
    assert isinstance(sent, basestring)

    tokens = word_tokenize(sent)
    return tagger.tag(tokens)


def passivep(tags):
    """Takes a list of tags, returns true if we think this is a passive
    sentence."""
    # Particularly, if we see a "BE" verb followed by some other, non-BE
    # verb, except for a gerund, we deem the sentence to be passive.

    postToBe = list(dropwhile( lambda(tag): not tag.startswith("BE"), tags))
    nongerund = lambda(tag): tag.startswith("V") and not tag.startswith("VBG")

    filtered = filter(nongerund, postToBe)
    out = any(filtered)

    return out


def oneline(sent):
    """Replace CRs and LFs with spaces."""
    return sent.replace("\n", " ").replace("\r", " ")


def print_if_passive(sent, tagger):
    """Given a sentence, tag it and print if we think it's a passive-voice
    formation."""
    tagged = tag_sentence(sent, tagger)
    tags = map(lambda (tup): tup[1], tagged)

    if passivep(tags):
        print "passive:", oneline(sent)
    else:
        print "active:", oneline(sent)


def print_is_passive(text):
    tagger = pos_tagger.get_tagger()
    punkt = tokenize.punkt.PunktSentenceTokenizer()
    sentences = punkt.tokenize(text)
    for sent in sentences:
        print_if_passive(sent, tagger)


def is_passive(sent, tagger):
    tagged = tag_sentence(sent, tagger)
    tags = map(lambda (tup): tup[1], tagged)
    if passivep(tags):
        return True
    return False


def count_passive_sentences(text, tagger):
    if text is None or text == '':
        return 0
    sentences = tokenize.punkt.PunktSentenceTokenizer().tokenize(text)
    num = 0
    for sent in sentences:
        if is_passive(sent, tagger):
            num += 1
    return num


# print count_passive_sentences("The book was sold yesterday.I went shopping yesterday. The kid was struck by a bus!")
