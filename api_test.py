import requests
import json

url = "http://127.0.0.1:8000/v1/offerings"
headers = {
    'Authorization': 'Api-Key ',
    'Content-Type': 'application/json'
}
payload = {
    # Add your payload data here
}

r = requests.post(url, headers=headers, data=json.dumps(payload))

print(r.text)