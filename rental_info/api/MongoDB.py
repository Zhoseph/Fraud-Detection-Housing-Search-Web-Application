from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

CRAWLERDBURI = 'mongodb://ec2-35-161-49-158.us-west-2.compute.amazonaws.com:27017/'
LISTDBURI = 'mongodb://ec2-52-25-0-66.us-west-2.compute.amazonaws.com:27017/'
CRAWLERDBCLIENT = MongoClient(CRAWLERDBURI)
LISTDBCLIENT = MongoClient(LISTDBURI)
try:
    CRAWLERDBCLIENT.server_info()
    #    LISTDBCLIENT.server_info()
    print "Connected successfully!!!"
except ConnectionFailure, e:
    print "Could not connect to MongoDB: %s" % e
