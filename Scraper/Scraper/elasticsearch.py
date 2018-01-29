from elasticsearch import Elasticsearch
try:
  es = Elasticsearch([{'host': 'us-west-2.compute.amazonaws.com', 'port': 9200}])
  print "Elasticsearch Connected", es.info()
except Exception as ex:
  print "Error:", ex