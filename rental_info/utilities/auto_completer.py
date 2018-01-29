# http://scottlobdell.me/2015/02/writing-autocomplete-engine-scratch-python/
from collections import defaultdict
from file_parser import file_to_set


class AutoCompleter(object):

    MIN_N_GRAM_SIZE = 3

    def __init__(self, words_file_path, min_results=10, max_results=20, score_threshold=0.4):
        self.words_file_path = words_file_path
        self.min_results = min_results
        self.max_results = max_results
        self.score_threshold = score_threshold
        places_set = file_to_set(self.words_file_path)
        self.token_to_place_name = defaultdict(list)
        self.n_gram_to_tokens = defaultdict(set)
        for place_name in places_set:
            place_name = place_name.lower().replace("-", " ").replace("(", " ").replace(")", " ").replace("'", " ")
            # tokens = place_name.split()
            # for token in tokens:
            self.token_to_place_name[place_name].append(place_name)
            for string_size in xrange(self.MIN_N_GRAM_SIZE, len(place_name) + 1):
                n_gram = place_name[:string_size]
                self.n_gram_to_tokens[n_gram].add(place_name)

    def get_words_file_path(self):
        return self.words_file_path

    def get_real_tokens_from_possible_n_grams(self, token):
        if token is None or token.isspace():
            return []
        real_tokens = []

        token_set = self.n_gram_to_tokens.get(token, set())
        real_tokens.extend(list(token_set))
        return real_tokens

    def get_scored_places_uncollapsed(self, real_tokens):
        places_scores = []
        for token in real_tokens:
            possible_places = self.token_to_place_name.get(token, [])
            for place_name in possible_places:
                score = float(len(token)) / len(place_name.replace(' ', ''))
                places_scores.append((place_name, score))
        return places_scores

    def filtered_results(self, places_scores):
        max_possibles = places_scores[:self.max_results]
        if places_scores and places_scores[0][1] == 1.0:
            return [places_scores[0][0]]

        possibles_within_thresh = [tuple_obj for tuple_obj in places_scores if tuple_obj[1] >= self.score_threshold]
        min_possibles = possibles_within_thresh if len(possibles_within_thresh) > self.min_results else max_possibles[
                                                                                                   :self.min_results]
        results = [tuple_obj[0] for tuple_obj in min_possibles]
        if results is None or len(results) == 0:
            return []
        results.sort(key=lambda x: x.lower())
        return results

    def guess_places(self, tokens):
        real_tokens = self.get_real_tokens_from_possible_n_grams(tokens)
        places_scores = self.get_scored_places_uncollapsed(real_tokens)
        collapsed_place_to_score = combined_place_scores(places_scores, len(tokens))
        places_scores = collapsed_place_to_score.items()
        places_scores.sort(key=lambda t: t[1], reverse=True)
        return self.filtered_results(places_scores)


def combined_place_scores(places_scores, num_tokens):
    collapsed_place_to_score = defaultdict(int)
    collapsed_place_to_occurence = defaultdict(int)
    if num_tokens == 0:
        return collapsed_place_to_occurence
    for place, score in places_scores:
        collapsed_place_to_score[place] += score
        collapsed_place_to_occurence[place] += 1
    for place in collapsed_place_to_score.keys():
        collapsed_place_to_score[place] *= collapsed_place_to_occurence[place] / float(num_tokens)
    return collapsed_place_to_score

# auto_completer = AutoCompleter('../data/words/places.txt')
# print auto_completer.guess_places('san ')
