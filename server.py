from config import environment
import requests
import json



url = "http://127.0.0.1:8000"
headers = {
    'Authorization': 'Api-Key ',
    'Content-Type': 'application/json'
}

def upload_to_server(items):
    requests.post(f'{url}/v1/offerings/update/', data=json.dumps(items), headers=headers)

# def upload_to_server(items):
#     for item in items:
#         try:
#             response = requests.post(f'{url}/v1/offerings/update/', data=json.dumps(item), headers=headers)
#                        #requests.post('%s/v1/offerings/update/' % environment.get('url'), data=json.dumps(items), headers=headers)
#             if response.status_code == 200:
#                 print(f"Item {item} uploaded successfully.")
#             else:
#                 print(f"Failed to upload item {item}. Server responded with status code: {response.status_code}")
#         except requests.exceptions.RequestException as e:
#             print(f"Failed to upload item {item}. Error: {e}")