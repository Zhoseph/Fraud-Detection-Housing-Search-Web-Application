import numpy as np
import requests
import simplejson as json
import utilities.text_analyzer as ta
from utilities.valuation_estimator import get_latest_price, INDICATORS
from feature.feature_selector import POSITIVE_WORDS, NEGATIVE_WORDS
import feature.feature_selector as feature_selector
from MongoDB import CRAWLERDBCLIENT
from math import sin, cos, sqrt, atan2, radians, fabs

# approximate radius of earth in km
R = 6373.0
ADDRESS_DISTANCE = 20  # meters
MIN_NUMBER_OF_IMAGES = 0
AVG_NUMBER_OF_IMAGES = 5
MIN_DESC_SCORE = -0.15 # based on experiments
MAX_DESC_SCORE = 0.17 # based on experiments

IMAGE_SEARCH_SERVER_URL = 'http://ec2-34-208-157-88.us-west-2.compute.amazonaws.com:5000/imagesearch/search'


def get_estimated_rent(zip_code, area):
    if isinstance(area, basestring):
        area = float(area)
    per_sqft_rent, latest_date = get_latest_price(zip_code, INDICATORS['rent_per_square_foot'])
    estimated_rent = per_sqft_rent * area
    return estimated_rent, latest_date


def check_price(estimated_rent, price):
    if price is None or price + (0.2 * estimated_rent) < estimated_rent:
        return 1
    elif price + (0.1 * estimated_rent) < estimated_rent:
        return 0.5
    elif price + (0.05 * estimated_rent) < estimated_rent:
        return 0.25
    return 0


# may need to pass the listid into the check_images and check_address method,
# check if crawler_listing_id in duplicate_image[] is listid in URL, do nothing, same as address_check
def check_images(image_array, listing_lat, listing_lon, price, list_id=None):
    if image_array is None or len(image_array) == 0:
        # No images, increase the score
        return 1, []
    if len(image_array) < AVG_NUMBER_OF_IMAGES:
        # less than avg number of images, increase the score
        image_score = (AVG_NUMBER_OF_IMAGES - len(image_array)) / float(AVG_NUMBER_OF_IMAGES)
        return image_score, []
    # issue a post request to image search server
    body = {'image_urls': image_array}
    response = requests.post(IMAGE_SEARCH_SERVER_URL, data=json.dumps(body))
    if response.status_code != 200:
        # there is a problem
        return 0, []

    json_data = json.loads(response.text)
    dup_images = json_data['duplicates']
    if dup_images is None or len(dup_images) == 0:
        return 0, []
    # check with crawler DB
    duplicated_image_url_set = set()
    score = 0
    crawler_collection = CRAWLERDBCLIENT.scrapy.scrapyItems
    for crawler_listing_id in dup_images:
        if list_id == crawler_listing_id:
            continue

        found_similar_listing = crawler_collection.find_one({'listid': crawler_listing_id})
        if found_similar_listing is None:
            continue
        # found at least one similar listing
        duplicated_image_url_set.add(found_similar_listing['url'])
        address_distance = find_distance(found_similar_listing['address']['lat'],
                                         found_similar_listing['address']['lon'],
                                         listing_lat, listing_lon)
        if address_distance > ADDRESS_DISTANCE:
            score += 1
        elif found_similar_listing['price'] is None or price is None or \
                        fabs(found_similar_listing['price'] - price) >= (0.1 * price):
            score += 1

    if score > 0:
        score = 2
    return score, list(duplicated_image_url_set)


def check_address(state, city, street, price, list_id=None):
    crawler_collection = CRAWLERDBCLIENT.scrapy.scrapyItems
    query_result = crawler_collection.find({'address.state': state,
                                            'address.city': city,
                                            'address.street': street})
    dup_address_set = set()
    for dup_address in query_result:
        # give urls of duplicate listings no matter what the price is, the price difference is only for scoring purpose
        if dup_address is None or dup_address['listid'] == list_id:
            continue
        dup_address_set.add(dup_address['url'])
        # if dup_address['price'] is None or price is None or \
        #                 fabs(dup_address['price'] - price) >= PRICE_DIFFERENCE:
    score = 0
    if len(dup_address_set) > 0:
        score = 1
    return score, list(dup_address_set)


def find_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return -1
    if lat1 == lat2 and lon1 == lon2:
        return 0
    # https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    rlat1 = radians(fabs(lat1))
    rlon1 = radians(fabs(lon1))
    rlat2 = radians(fabs(lat2))
    rlon2 = radians(fabs(lon2))

    dlon = rlon2 - rlon1
    dlat = rlat2 - rlat1

    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # distance in km
    distance = R * c
    # return distance in meters
    return distance * 1000


def check_description(description, scaler, model):
    # create a normalized feature vector
    if description is None or len(description) == 0:
        return 1
    new_data = feature_selector.get_features(description)
    scaled_features = scaler.transform(np.array(new_data).reshape(1, -1))
    # find the score; the lower the more likely it is an outlier
    raw_desc_score = model.decision_function(scaled_features)
    desc_score = round(raw_desc_score[0], 4)
    scaled_desc = (MAX_DESC_SCORE - desc_score)/(MAX_DESC_SCORE - MIN_DESC_SCORE)
    return round(scaled_desc, 3)


def get_positive_negative_words(description):
    word_list = ta.cleanup_text(description, ta.STOP_WORDS, True)
    if word_list is None or len(word_list) == 0:
        return [], []
    positive_words = set()
    negative_words = set()
    for w in word_list:
        if w in POSITIVE_WORDS:
            positive_words.add(w)
        if w in NEGATIVE_WORDS:
            negative_words.add(w)
    return list(positive_words), list(negative_words)
