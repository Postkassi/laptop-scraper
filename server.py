from config import environment
import requests
import json

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Api-Key %s' % (environment.get('api_key'),)
}

def upload_to_server(items):
    requests.post('%s/v1/offerings/update/' % environment.get('url'), data=json.dumps(items), headers=headers)