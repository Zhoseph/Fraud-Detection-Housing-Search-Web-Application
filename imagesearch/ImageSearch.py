import base64
import requests
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify, abort
from elasticsearch import Elasticsearch
import json
from flask import abort
from celery import Celery

app = Flask(__name__)
app.config['version'] = 'Version 1.0'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celeryClient = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celeryClient.conf.update(app.config)

try:
  es = Elasticsearch([{'host': 'AWS', 'port': 9200}])
  print "Connected", es.info()
except Exception as ex:
  print "Error:", ex

@app.route('/')
def index():
    return "Image Search Server"

@app.route('/imagesearch/storedata', methods=['GET'])
def get_tasks():
    imageurl = request.args.get('imageurl', "")
    listid = request.args.get('listid', "")
    basecode = get_as_base64(imageurl);
    image = {
        'listid': listid,
        'img': basecode,
        'imageurl': imageurl
    }
    res = es.index(index='imagesearch', doc_type='images', body=image)
    return jsonify(res)

@app.route('/imagesearch/search', methods=['GET', 'POST'])
def get_image():
        data = request.get_data()
        imagelist = json.loads(data)
        if imagelist['image_urls'] is None:
                abort(400, 'Image_urls can not be None')
        task = check_image_dup.delay(imagelist['image_urls'])
        return jsonify({"status": "received request", "taskid":task.id}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

@celeryClient.task(bind=True)
def check_image_dup(self,imageArray):
        resultList = []
        i = 1
        for imageurl in imageArray:
                try:
                        basecode = get_as_base64(imageurl);
                        query = { "min_score": 0.36, "query":{"image":{"img":{ "feature": "JCD", "image": basecode}}}}
                        res = es.search(index="imagesearch", doc_type="images", body=query, request_timeout=60)
                        for hit in res['hits']['hits']:
                                listid = hit['_source']['listid']
                                resultList.append(listid)
                        self.update_state(state='PROGRESS', meta={'current': i, 'status' : 'checking duplicate image' })
                        i = i+1
                except Exception:
            # Dont exit the loop but continue with others
                        pass
        return {'total': str(i),'status': 'Task completed!', 'duplicates':list(set(resultList))}

@app.route('/imagesearch/status/<task_id>')
def taskstatus(task_id):
    task = check_image_dup.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'checking duplicate image'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            'duplicates': task.info.get('duplicates', '')
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return jsonify({"error":error}), 500

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)