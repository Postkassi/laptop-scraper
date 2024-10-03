import config
import requests
import json

api_key = "5nvH4awp.g8PwVowibW9iq7OU0mucEqsDhbVcY3NZ"

url = "http://127.0.0.1:8000"

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Api-Key ' '5nvH4awp.g8PwVowibW9iq7OU0mucEqsDhbVcY3NZ',
}

def upload_to_server(items):
    for item in items:
        try:
            response = requests.post(f'http://127.0.0.1:8000/v1/offerings/update/', data=json.dumps(item), headers=headers)
            if response.status_code == 200:
                print(f"Item {item} uploaded successfully.")
            else:
                print(f"Failed to upload item {item}. Server responded with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload item {item}. Error: {e}")