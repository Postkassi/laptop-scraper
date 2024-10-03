from config import environment
import requests
import json

url = "http://127.0.0.1:8000/v1/offerings/update/"
headers = { 
        'Authorization':'Api-Key %s' % '5nvH4awp.g8PwVowibW9iq7OU0mucEqsDhbVcY3NZ',
        'Content-Type': 'application/json'
        }

# Define the URL of the API
#url = "http://127.0.0.1:8000/v1/offerings"
#header = { 'Authorization':'Bearer mWuzO42I.Bv88GxkwuZuNoSO9nJuXodOf0VcwlMVP'}

def upload_to_server(items):
    for item in items:
        try:
            r = requests.post(url,data=json.dumps(item), headers=headers, )
            if r.status_code == 200:
                print(f"Item {item} uploaded successfully.")
            else:
                print(f"Failed to upload item {item}. Server responded with status code: {r.status_code} and also: {r.text}")
        except r.exceptions.RequestException as e:
            print(f"Failed to upload item {item}. Error: {e}")