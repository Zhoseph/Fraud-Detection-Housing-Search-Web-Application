#!flask/bin/python
from flask import Flask
from flask import Response
from flask import jsonify
import simplejson as json
from bs4 import BeautifulSoup
from error import InvalidUsage
import requests
from utilities.valuation_estimator import get_latest_price
from utilities.valuation_estimator import INDICATORS
from metadata import attribute_names
from models.data_prepration import ScaleMethod
from utilities.text_analyzer import ARTICLE_SET
import models.isolation_forest as isolation_forest
import feature.feature_selector as feature_selector
import utilities.file_parser as file_parser
# crawler db
from MongoDB import CRAWLERDBCLIENT

# listing db
# from MongoDB import LISTDBCLIENT

app = Flask(__name__)
app.config['version'] = 'Version 1.0'


@app.route('/')
def index():
    return "An online rental listing application"


# GET /api/fraud/listing/{listing_id}
@app.route('/api/fraud/listing/<int:listing_id>')
def check_for_fraud(listing_id):
    # score is 0 to 5, 0 meaning that it is not a scam
    score = 0.0
    try:
        # CrawlerDB Collection
        crawlercolletion = CRAWLERDBCLIENT.scrapy.scrapyItems
        # TODO fetch the listing details from listing database
        # listcollection = LISTDBCLIENT.db.collection
        # json_listing = listcollection.find_one({"listing_id" : listing_id})
        # if json_listing is None:
        # abort()
        json_listing = file_parser.file_to_json('listing.json')
        description = json_listing['description']
        address = json_listing['address']
        area = json_listing['area']  # in sqft
        price = json_listing['price']  # Important: assumption is that price is rent/month
        image_array = json_listing['image']

        # 2- find the estimated rent
        estimated_rent = 0
        latest_date = ''
        if address is None:
            score += 2  # increase the fraud score
        else:
            zip_code = address['zip_code']
            # TODO if no zip code use other parameters of the address to find the zip code
            per_sqft_rent, latest_date = get_latest_price(zip_code, INDICATORS['rent_per_square_foot'])
            estimated_rent = per_sqft_rent * area

        # if listed price is significantly lower than the estimated rent, increase the score
        # TODO significant is equal to $100 here, check for adjustments
        if price < estimated_rent - 100:
            score += 1

        # 2- check images
        # duplicated_listings = []
        imageDuplicates = []
        imageDuplicateURL = []
        # for filtering out the lists with same picture but different address
        imageDupSameAddress = []
        addressDuplicates = []
        addressDuplicateURL = []
        if image_array is None or len(image_array) == 0:
            # if there are no images, increase the score
            score += 2
        elif len(image_array) < 3:
            # if there are less than 3 images increase the score
            score += 1
        if len(image_array) > 0:
            # request for image duplications from image search server
            # TODO issue a post request to image search server - done
            url = 'http://ec2-34-208-24-106.us-west-2.compute.amazonaws.com:5000/imagesearch/search'
            body = {'image_urls': image_array}
            response = requests.post(url, data=json.dumps(body))
            imageDupDifAddress = []
            if response.status_code is 200:
                json_data = json.loads(response.text)
                imageDuplicates = json_data['duplicates']
            if imageDuplicates is not None and len(imageDuplicates) > 0:
                for crawler_listing_id in imageDuplicates:
                    # TODO query crawler database with id
                    duplicateListing = crawlercolletion.find_one({'listid': crawler_listing_id})
                    # json_image_info = file_parser.file_to_json('crawler.json')
                    # need to check if both listing has address stored in DB
                    # compare addresses
                    if duplicateListing is None:
                        continue
                    imageDuplicateURL.append(duplicateListing['url'])
                    if duplicateListing['address']['street_address'] is not None and address['street'] is not None:
                        if duplicateListing['address']['state'] == address['state']:
                            score += 1
                            imageDupDifAddress.append(crawler_listing_id)
                        else:
                            if duplicateListing['address']['city'] == address['city']:
                                score += 1
                                imageDupDifAddress.append(crawler_listing_id)
                            else:
                                # should check if street address is similar, may not identical reference:
                                # https://stackoverflow.com/questions/31642940/finding-if-two-strings-are-almost-similar
                                if duplicateListing['address']['street_address'] == address['street']:
                                    score += 1
                                    imageDupDifAddress.append(crawler_listing_id)
                                else:
                                    # if address is same then compare price
                                    if duplicateListing['price'] is not None and price is not None:
                                        # there should be a price gap, may be slight different on different platform
                                        if price < duplicateListing['price'] - 50:
                                            score += 1
                # filter the duplicateds with same image and same address
                imageDupSameAddress = list(set(imageDuplicates) - set(imageDupDifAddress))
                # else:
        # TODO query crawler database with address
        if address is not None:
            queryResult = crawlercolletion.find({'address.state': address['state'], 'address.city': address['city'],
                                                 'address.street': address['street']})
            addressdup = []
            for listingResult in queryResult:
                addressdup.append(listingResult['listid'])
                addressDuplicateURL.append(listingResult['url'])
            # get listid of same address but different images
            addressDuplicates = list(set(addressdup) - set(imageDupSameAddress))

        if score < 5:
            # 3- check description
            soup = BeautifulSoup(description, 'lxml')
            document = soup.get_text()
            fs = feature_selector.FeatureSelector(document, ARTICLE_SET)
            # if word count of the description is zero, increase the score
            if fs.get_word_count() == 0:
                score += 1
            else:
                # TODO check with the trained model
                score += 0.12345

        json_resp = json.dumps({'listing_id': listing_id,
                                'score': score,
                                "avg_price": {
                                    "price": estimated_rent,
                                    "latest_date": latest_date
                                },
                                'duplicated_listings': [
                                    {
                                        "type": "image",
                                        "duplicates": imageDuplicateURL
                                    },
                                    {
                                        "type": "address",
                                        "duplicates": addressDuplicateURL
                                    }
                                ],
                                'positive_words': [],
                                'negative_words': []
                                })

        resp = Response(json_resp, status=200, mimetype='application/json')
        return resp
    except Exception, e:
        # TODO Fix the error code
        raise InvalidUsage(str(e), status_code=500)


# Reference: http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/info')
def app_status():
    return json.dumps({'server_info': app.config['version']})


@app.before_first_request
def run_on_start():
    try:
        iso_model = isolation_forest.IsolationForestModel('../data/results/features_just_data.csv',
                                                          attribute_names.FEATURE_NAMES,
                                                          0.001,
                                                          ScaleMethod.Normalize)
    except Exception, e:
        pass  # run app service


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
