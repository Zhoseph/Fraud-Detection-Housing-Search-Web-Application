# coding:utf-8
"""
scrapy-mongodb - MongoDB pipeline for Scrapy
Homepage: https://github.com/sebdah/scrapy-mongodb
Author: Sebastian Dahlgren <sebastian.dahlgren@gmail.com>
License: Apache License 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>
Copyright 2013 Sebastian Dahlgren
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import datetime

from pymongo import errors
from pymongo.mongo_client import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pymongo.read_preferences import ReadPreference

from scrapy import log
from scrapy.contrib.exporter import BaseItemExporter
import requests
import json
# import treq
# from klein import Klein
# from twisted.internet.defer import inlineCallbacks, returnValue
from httplib2 import Http
import urllib
import base64
from elaconn import es
from time import sleep

VERSION = '0.9.1'

frauddetectionurl = 'http://54.193.92.20/api/fraud/search'
uiEmailUrl = "http://54.175.222.115:8888/fraud_report"


# uiEmailUrl = "http://cmpe281-project-2-dora-jia.c9users.io/fraud_report"
def not_set(string):
    """ Check if a string is None or ''
    :returns: bool - True if the string is empty
    """
    if string is None:
        return True
    elif string == '':
        return True
    return False


class MongoDBPipeline(BaseItemExporter):
    """ MongoDB pipeline class """
    # Default options
    config = {
        'uri': 'mongodb://mongodb://us-west-2.compute.amazonaws.com:27017',
        'fsync': False,
        'write_concern': 0,
        'database': 'scrapy-mongodb',
        'collection': 'items',
        'replica_set': None,
        'unique_key': None,
        'buffer': None,
        'append_timestamp': False,
        'stop_on_duplicate': 0,
    }

    # Item buffer
    current_item = 0
    item_buffer = []

    # Duplicate key occurence count
    duplicate_key_count = 0

    def load_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings

        # Versions prior to 0.25
        if not hasattr(spider, 'update_settings') and hasattr(spider, 'custom_settings'):
            self.settings.setdict(spider.custom_settings or {}, priority='project')

    def open_spider(self, spider):
        self.load_spider(spider)

        # Configure the connection
        self.configure()

        if self.config['replica_set'] is not None:
            connection = MongoReplicaSetClient(
                self.config['uri'],
                replicaSet=self.config['replica_set'],
                w=self.config['write_concern'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY_PREFERRED)
        else:
            # Connecting to a stand alone MongoDB
            connection = MongoClient(
                self.config['uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)

        # Set up the collection
        database = connection[self.config['database']]
        self.collection = database[self.config['collection']]
        log.msg(u'Connected to MongoDB {0}, using "{1}/{2}"'.format(
            self.config['uri'],
            self.config['database'],
            self.config['collection']))

        # Ensure unique index
        if self.config['unique_key']:
            self.collection.ensure_index(self.config['unique_key'], unique=True)
            log.msg(u'Ensuring index for key {0}'.format(
                self.config['unique_key']))

        # Get the duplicate on key option
        if self.config['stop_on_duplicate']:
            tmpValue = self.config['stop_on_duplicate']
            if tmpValue < 0:
                log.msg(
                    (
                        u'Negative values are not allowed for'
                        u' MONGODB_STOP_ON_DUPLICATE option.'
                    ),
                    level=log.ERROR
                )
                raise SyntaxError(
                    (
                        'Negative values are not allowed for'
                        ' MONGODB_STOP_ON_DUPLICATE option.'
                    )
                )
            self.stop_on_duplicate = self.config['stop_on_duplicate']
        else:
            self.stop_on_duplicate = 0

    def configure(self):
        """ Configure the MongoDB connection """
        # Handle deprecated configuration
        if not not_set(self.settings['MONGODB_HOST']):
            log.msg(
                u'DeprecationWarning: MONGODB_HOST is deprecated',
                level=log.WARNING)
            mongodb_host = self.settings['MONGODB_HOST']

            if not not_set(self.settings['MONGODB_PORT']):
                log.msg(
                    u'DeprecationWarning: MONGODB_PORT is deprecated',
                    level=log.WARNING)
                self.config['uri'] = 'mongodb://{0}:{1:i}'.format(
                    mongodb_host,
                    self.settings['MONGODB_PORT'])
            else:
                self.config['uri'] = 'mongodb://{0}:27017'.format(mongodb_host)

        if not not_set(self.settings['MONGODB_REPLICA_SET']):
            if not not_set(self.settings['MONGODB_REPLICA_SET_HOSTS']):
                log.msg(
                    (
                        u'DeprecationWarning: '
                        u'MONGODB_REPLICA_SET_HOSTS is deprecated'
                    ),
                    level=log.WARNING)
                self.config['uri'] = 'mongodb://{0}'.format(
                    self.settings['MONGODB_REPLICA_SET_HOSTS'])

        # Set all regular options
        options = [
            ('uri', 'MONGODB_URI'),
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('database', 'MONGODB_DATABASE'),
            ('collection', 'MONGODB_COLLECTION'),
            ('replica_set', 'MONGODB_REPLICA_SET'),
            ('unique_key', 'MONGODB_UNIQUE_KEY'),
            ('buffer', 'MONGODB_BUFFER_DATA'),
            ('append_timestamp', 'MONGODB_ADD_TIMESTAMP'),
            ('stop_on_duplicate', 'MONGODB_STOP_ON_DUPLICATE')
        ]

        for key, setting in options:
            if not not_set(self.settings[setting]):
                self.config[key] = self.settings[setting]

        # Check for illegal configuration
        if self.config['buffer'] and self.config['unique_key']:
            log.msg(
                (
                    u'IllegalConfig: Settings both MONGODB_BUFFER_DATA '
                    u'and MONGODB_UNIQUE_KEY is not supported'
                ),
                level=log.ERROR)
            raise SyntaxError(
                (
                    u'IllegalConfig: Settings both MONGODB_BUFFER_DATA '
                    u'and MONGODB_UNIQUE_KEY is not supported'
                ))

    def process_item(self, item, spider):
        """ Process the item and add it to MongoDB
        :type item: Item object
        :param item: The item to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        item = dict(self._get_serialized_fields(item))

        if self.config['buffer']:
            self.current_item += 1

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

            self.item_buffer.append(item)

            if self.current_item == self.config['buffer']:
                self.current_item = 0
                return self.insert_item(self.item_buffer, spider)

            else:
                return item

        return self.insert_item(item, spider)

    def close_spider(self, spider):
        """ Method called when the spider is closed
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: None
        """
        if self.item_buffer:
            self.insert_item(self.item_buffer, spider)

    def insert_item(self, item, spider):
        """ Process the item and add it to MongoDB
        :type item: (Item object) or [(Item object)]
        :param item: The item(s) to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        if not isinstance(item, list):
            item = dict(item)

            if self.config['append_timestamp']:
                item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

        if self.config['unique_key'] is None:
            try:
                self.collection.insert(item, continue_on_error=True)
                log.msg(
                    u'Stored item(s) in MongoDB {0}/{1}'.format(
                        self.config['database'], self.config['collection']),
                    level=log.INFO,
                    spider=spider)

            except errors.DuplicateKeyError:
                log.msg(u'Duplicate key found', level=log.INFO)
                if (self.stop_on_duplicate > 0):
                    self.duplicate_key_count += 1
                    if (self.duplicate_key_count >= self.stop_on_duplicate):
                        self.crawler.engine.close_spider(
                            spider,
                            'Number of duplicate key insertion exceeded'
                        )
                pass

        else:
            key = {}
            if isinstance(self.config['unique_key'], list):
                for k in dict(self.config['unique_key']).keys():
                    key[k] = item[k]
            else:
                key[self.config['unique_key']] = item[self.config['unique_key']]
            query = self.collection.find_one(key)
            if query == None:
                try:
                    self.collection.insert_one(item)
                    log.msg(
                        u'Stored item(s) {0} in MongoDB {1}/{2}'.format(item['listid'],
                                                                        self.config['database'],
                                                                        self.config['collection']),
                        level=log.INFO,
                        spider=spider)
                    imageSet = item['image']
                    for value in imageSet:
                        response = storeImage(value, item['listid'])
                        log.msg(
                            u'Stored image(s) in ElasticSearch {0}'.format(
                                response),
                            level=log.INFO,
                            spider=spider)
                        sleep(5)
                except Exception, e:
                    log.msg(
                        u'Stored list {0} failed because of error: {1}'.format(
                            item['listid'], str(e)),
                        level=log.ERROR,
                        spider=spider)
            else:
                if query["website"] == "Craiglist":
                    self.collection.update_one({'listid': item['listid']}, {
                        "$set": {'isRemoved': item['isRemoved'], 'isFlagged': item['isFlagged']}}, upsert=False)
                    log.msg(
                        u'Listing {0} is updated for Craiglist'.format(item['listid']),
                        level=log.INFO,
                        spider=spider)
                else:
                    self.collection.update(key, item, upsert=True)
                    log.msg(
                        u'Listing {0} is updated'.format(item['listid']),
                        level=log.INFO,
                        spider=spider)
            if spider.name is "universalSpider":
                callFraudDetection(item['listid'], spider)
        return item


def callFraudDetection(listid, spider):
    try:
        params = {"crawler_listing_id": listid, "email_address": spider.email_address}
        # r = treq.get(frauddetectionurl, params=params)
        # r.addCallback(print_response)
        response = requests.get(frauddetectionurl, params=params)
        if response.status_code != 200:
            data = {
                "error": "No fraud detection report!"
            }
            log.msg(
                u'Sending list {0} to fraud detection server failed'.format(listid),
                level=log.INFO,
                spider=spider)
        if response.status_code is 200:
            data = json.loads(response.text)
            log.msg(
                u'Sending list {0} to fraud detection server succeed'.format(listid),
                level=log.INFO,
                spider=spider)
        http_obj = Http()
        resp, content = http_obj.request(
            uri=uiEmailUrl,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json.dumps(data),
        )
        log.msg(
            u'Sending list {0} to UI fraud report server is {1}'.format(listid, resp),
            level=log.INFO,
            spider=spider)
    except Exception, e:
        log.msg(
            u'Error happens in generating fraud detection report: {0}'.format(str(e)),
            level=log.ERROR)


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)


def storeImage(imageurl, listid):
    try:
        basecode = get_as_base64(imageurl);
        image = {
            'listid': listid,
            'img': basecode,
            'imageurl': imageurl
        }
        res = es.index(index='imagesearch', doc_type='images', body=image)
        return res['created']
    except Exception, e:
        log.msg(
            u'Error happens in storing images: {0}'.format(str(e)),
            level=log.ERROR)
        return "False"

# def print_response(response):
#    deferred = treq.json_content(response)
#    fraudreport = requests.post(uiEmailUrl,data=json.dumps(deferred))
#    log.msg(
#        u'Sending list to UI fraud report server is {1}'.format(fraudreport),
#        level=log.DEBUG)
#    return deferred

