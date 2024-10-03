import config
import requests
import json

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Api-Key %s' % config.dev["APIKEY"],
}

def upload_to_server(items):
    requests.post('http://127.0.0.1:8000/v1/offerings/update/' , config.dev["APIKEY"], data=json.dumps(items), headers=headers)