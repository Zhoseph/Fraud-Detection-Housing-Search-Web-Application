from sklearn.externals import joblib
from flask import Flask
from flask import Response
from flask import request
import simplejson as json
import fraud_algorithm as algorithm
from utilities.auto_completer import AutoCompleter
from MongoDB import LISTDBCLIENT
from MongoDB import CRAWLERDBCLIENT
from bson.objectid import ObjectId
from bson import json_util
import logging
from celery import Celery
from httplib2 import Http

uiEmailUrl = 'http://54.175.222.115:8888/fraud_report'
uiListingUrl = 'http://52.25.0.66:3100/writereport'

app = Flask(__name__)
app.config['version'] = 'Version 1.0'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celeryClient = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celeryClient.conf.update(app.config)

global clf
clf = joblib.load('/home/ubuntu/flaskapp/model_isof.pkl')

global minmax
minmax = joblib.load('/home/ubuntu/flaskapp/minmax.pkl')

global autocompleter
autocompleter = AutoCompleter('/home/ubuntu/data/words/places.txt')

@app.route('/')
def index():
    return "Fraud detection Flask application"


# GET /api/fraud/listing/{listing_id}
@app.route('/api/fraud/listing/<listing_id>')
def calculate_listing_score(listing_id):
    print 'querying listing with id %s' % listing_id
    print 'listing id is: %s' % listing_id
    searchScrapedListings.apply_async(args=[listing_id])
    return json.dumps({"status": "updating"})


@celeryClient.task
def searchScrapedListings(listing_id):
    listing_collection = LISTDBCLIENT.globallisting.listings
    json_listing = None
    try:
        print 'query listing db ...'
        json_listing = listing_collection.find_one({'_id': ObjectId(listing_id)})
    except Exception, e:
        print str(e)
        logging.getLogger().debug(str(e))
        # raise e
        return Response(json.dumps({'error': str(e)}), status=404, mimetype='application/json')
    if json_listing is None:
        print 'the listing was not found :-( '
        logging.getLogger().debug('Can not find the listing with id %s' % listing_id)
        # raise Exception('Can not find the listing')
        return json.dumps({'error': 'the listing was not found :-( '})

    # score is 0 to 5, 0 meaning that it is not a scam
    score = 0.0
    estimated_rent = 0.0
    latest_date = ''
    positive_words = []
    negative_words = []
    duplicated_image = []
    duplicated_address = []

    address_score = 0
    price_score = 0
    image_score = 0
    desc_score = 0
    print 'Let\'s do something! listing id: %s' % listing_id
    print(json.dumps(json_listing, default=json_util.default, indent=4))
    try:
        # ADDRESS
        address = json_listing['address']
        if address is None:
            # No address, increase the score
            address_score += 3
        else:
            if address['zipcode'] is None:
                address_score += 1
            else:
                try:
                    # RENT PRICE
                    print 'Rent price ...'
                    print 'Zip code is: %s' % address['zipcode']
                    estimated_rent, latest_date = algorithm.get_estimated_rent(address['zipcode'], json_listing['area'])
                    price_score += algorithm.check_price(estimated_rent, json_listing['price'])
                except Exception, e:
                    logging.getLogger().error('Can not calculate the estimated price for the '
                             'listing with id %s. %s' % (listing_id, str(e)))
            try:
                # DUPLICATE IMAGES
                print 'Duplicate images ...'
                image_score, duplicated_image = algorithm.check_images(json_listing['image'],
                                                                  address['lat'],
                                                                   address['lon'],
                                                                   json_listing['price'])
            except Exception, e:
                logging.getLogger().error('Can not search images for the '
                         'listing with id %s. %s' % (listing_id, str(e)))
                image_score += 1
            # DUPLICATE ADDRESS
            print 'Duplicate address ...'
            try:
                address_score, duplicated_address = algorithm.check_address(address['state'],
                                                                            address['city'],
                                                                            address['street'],
                                                                            json_listing['price'])
            except Exception, e:
                logging.getLogger().error('Can not parse the address of the listing with id %s.' % listing_id)
        try:
            # DESCRIPTION
            print 'Description ....'
            description = json_listing['description']
            desc_score = algorithm.check_description(description, minmax, clf)
            # get positive and negative words
            positive_words, negative_words = algorithm.get_positive_negative_words(description)
        except Exception, e:
            logging.getLogger().error('Can not parse the description of the listing with id %s.' % listing_id)
        score = address_score + price_score + image_score + desc_score
        json_resp = json.dumps({'listing_id': listing_id,
                                'score': round(score, 3),
                                'address_score': address_score,
                                'price_score': price_score,
                                'image_score': image_score,
                                'description_score': desc_score,
                                'avg_price': {
                                    'price': round(estimated_rent,2),
                                    'latest_date': latest_date
                                },
                                'duplicated_listings': [
                                    {
                                        'type': 'image',
                                        'duplicates': duplicated_image
                                    },
                                    {
                                        'type': 'address',
                                        'duplicates': duplicated_address
                                    }
                                ],
                                'positive_words': positive_words,
                                'negative_words': negative_words
                                })
        http_obj = Http()
        resp, content = http_obj.request(
            uri=uiListingUrl,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json_resp
        )
        return resp
    except Exception, e:
        #raise e
        return json.dumps({'error': str(e)})


@app.route('/api/fraud/search', methods=['GET'])
def calculate_scraped_listing_score():
    crawler_listing_id = request.args.get('crawler_listing_id')
    print 'listing id is: %s' % crawler_listing_id
    email_address = request.args.get('email_address')
    calculateScore.apply_async(args=[crawler_listing_id, email_address])
    return json.dumps({"status": "updating"})


@celeryClient.task
def calculateScore(crawler_listing_id, email_address):
    crawler_collection = CRAWLERDBCLIENT.scrapy.scrapyItems
    try:
        json_listing = crawler_collection.find_one({'listid': crawler_listing_id})
    except Exception, e:
        logging.getLogger().debug(str(e))
        return Response(json.dumps({'error': str(e)}), status=404, mimetype='application/json')
    if json_listing is None:
        logging.getLogger().debug('Can not find the listing with id %s' % crawler_listing_id)
        return json.dumps({'error': 'Can not find the listing'})

    # score is 0 to 5, 0 meaning that it is not a scam
    score = 0.0
    estimated_rent = 0.0
    latest_date = ''
    positive_words = []
    negative_words = []
    duplicated_image = []
    duplicated_address = []

    address_score = 0
    price_score = 0
    image_score = 0
    desc_score = 0
    try:
        listing_url = json_listing['url']
        # ADDRESS
        address = json_listing['address']
        if address is None:
            # No address, increase the score
            address_score += 3
        else:
            if address['zipcode'] is None:
                address_score += 1
            else:
                # RENT PRICE
                try:
                    estimated_rent, latest_date = algorithm.get_estimated_rent(address['zipcode'], json_listing['area'])
                    price_score += algorithm.check_price(estimated_rent, json_listing['price'])
                except Exception, e:
                    logging.getLogger().error('Can not calculate the estimated price for the '
                             'listing with id %s. %s' % (crawler_listing_id, str(e)))
            try:
                # DUPLICATE IMAGES
                image_score, duplicated_image = algorithm.check_images(json_listing['image'],
                                                                   address['lat'],
                                                                   address['lon'],
                                                                   json_listing['price'],
                                                                   crawler_listing_id)
            except Exception, e:
                logging.getLogger().error('Can not search images for the '
                                      'listing with id %s. %s' % (crawler_listing_id, str(e)))
                image_score += 1
            # DUPLICATE ADDRESS
            try:
                address_score, duplicated_address = algorithm.check_address(address['state'],
                                                                         address['city'],
                                                                         address['street'],
                                                                         json_listing['price'],
                                                                         crawler_listing_id)
            except Exception, e:
                logging.getLogger().error('Can not parse the address of the listing with id %s.' % crawler_listing_id)
        
        try:
            # DESCRIPTION
            description = json_listing['description']
            desc_score = algorithm.check_description(description, minmax, clf)
            print score
            print desc_score
            print score

            # get positive and negative words
            positive_words, negative_words = algorithm.get_positive_negative_words(description)
        except Exception, e:
            logging.getLogger().error('Can not parse the description of the listing with id %s.' % crawler_listing_id)
        score = address_score + price_score + image_score + desc_score
        json_resp = json.dumps({'listing_id': crawler_listing_id,
                                'email_address': email_address,
                                'listing_url': listing_url,
                                'score': round(score, 3),
                                'address_score': address_score,
                                'price_score': price_score,
                                'image_score': image_score,
                                'description_score': desc_score,
                                'avg_price': {
                                    'price': round(estimated_rent,2),
                                    'latest_date': latest_date
                                },
                                'duplicated_listings': [
                                    {
                                        'type': 'image',
                                        'duplicates': duplicated_image
                                    },
                                    {
                                        'type': 'address',
                                        'duplicates': duplicated_address
                                    }
                                ],
                                'positive_words': positive_words,
                                'negative_words': negative_words
                               })
        http_obj = Http()
        resp, content = http_obj.request(
            uri=uiEmailUrl,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json_resp,
        )
        return resp                            
    except Exception, e:
        return json.dumps({'error': str(e)})


@app.route('/api/search/autocompletion', methods=['GET'])
def autocomplete_token():
    try:
        token = request.args.get('token')
        results = autocompleter.guess_places(token.lower())
        json_resp = json.dumps({'suggested_tokens': results})
        #resp = Response(json_resp, status=200, mimetype='application/json')
        return json_resp
    except Exception, e:
        return json.dumps({'error': str(e)})


# POST /api/fraud/description
@app.route('/api/fraud/description', methods=['POST'])
def calculate_description_score():
    try:
        json_request = request.json
        description = json_request['description']
        desc_score = algorithm.check_description(description, minmax, clf)

        json_resp = json.dumps({'description': description, 'score': desc_score})
        #resp = Response(json_resp, status=200, mimetype='application/json')
        return json_resp
    except Exception, e:
        return json.dumps({'error': 'Internal server error'})


# POST /api/fraud/price
@app.route('/api/fraud/rent', methods=['POST'])
def calculate_estimated_price():
    try:
        json_request = request.json
        zip_code = json_request['zipcode']
        area = json_request['area']
        estimated_rent, latest_date = algorithm.get_estimated_rent(zip_code, area)

        json_resp = json.dumps({'area': area, 'zipcode': zip_code,
                                'estimated_rent': estimated_rent,
                                'latest_date': latest_date})
        #resp = Response(json_resp, status=200, mimetype='application/json')
        return json_resp
    except Exception, e:
        logging.getLogger().debug(str(e))
        return json.dumps({'error': str(e)})


@app.before_first_request
def run_on_start():
    print 'Received the first scoring request!'


if __name__ == "__main__":
    #    from sklearn.externals import joblib
    print 'Started running!'
    #    clf = joblib.load('model_isof.pkl')
    #    minmax = joblib.load('minmax.pkl')
    #    standard = joblib.load('standard.pkl')
    # set up a logger
    logging.basicConfig(filename='/home/ubuntu/logs/fraud.log',
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG)
    # get the root logger
    # logger = logging.getLogger()
    app.run()

