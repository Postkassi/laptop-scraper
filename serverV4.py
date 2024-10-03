import config
import requests
import json

url = "http://127.0.0.1:8000"

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Api-Key %s' %  '5nvH4awp.g8PwVowibW9iq7OU0mucEqsDhbVcY3NZ',
}

def check_and_upload_item(item):
    # Check if the item exists in the database
    response = requests.post('http://127.0.0.1:8000/v1/offerings/', params={'code': item['code']}, headers=headers)
    
    if response.status_code == 404:
        # Item does not exist, prompt the user to create it
        print(f"Item with code {item['code']} does not exist.")
        create = input("Do you want to create this item? (yes/no): ").strip().lower()
        
        if create == 'yes':
            # Collect additional information if needed
            item['name'] = input("Enter the name for the item: ").strip()
            # Add more fields as necessary
            
            # Upload the new item to the server
            response = requests.post('http://127.0.0.1:8000/v1/offerings/update/', data=json.dumps(item), headers=headers)
            if response.status_code == 201:
                print("Item created successfully.")
            else:
                print("Failed to create item:", response.text)
        else:
            print("Item creation skipped.")
    elif response.status_code == 200:
        # Item exists, proceed with the update
        response = requests.post('http://127.0.0.1:8000/v1/offerings/update/', data=json.dumps(item), headers=headers)
        if response.status_code == 200:
            print("Item updated successfully.")
        else:
            print("Failed to update item:", response.text)
    else:
        print("Error checking item:", response.text)

def upload_to_server(items):
    for item in items:
        check_and_upload_item(item)

# Example usage
items = [
    {'code': 'item1', 'other_field': 'value1'},
    {'code': 'item2', 'other_field': 'value2'},
    # Add more items as needed
]

upload_to_server(items)