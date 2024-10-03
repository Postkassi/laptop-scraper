import re
import requests
import json
from time import sleep
from bs4 import BeautifulSoup

from retailers import retailer_urls

# Add a timer between requests, so the websites don't forcibly close our connection
TIMER = 2 # seconds
def wait_between_requests(r, *args, **kwargs):
    sleep(TIMER)

request_session = requests.Session()
request_session.hooks['response'].append(wait_between_requests)

def extract_items_from_url(url, retailer):
    items = []
    baseurl = retailer_urls.get(retailer).get('baseurl')

    if (retailer == 'advania'):
        return advania_parser(url, retailer, baseurl, items)
    elif (retailer == 'tolvutek'):
         return tolvutek_parser(url, retailer, baseurl, items)
    elif (retailer == 'computer'):
         return computer_parser(url, retailer, baseurl, items)
    elif (retailer == 'elko'):
         return elko_parser(url, retailer, baseurl, items)
    elif (retailer == 'kisildalur'):
         return kisildalur_parser(url, retailer, baseurl, items)
    elif (retailer == 'macland'):
         return macland_parser(url, retailer, baseurl, items)
    elif (retailer == 'opinkerfi'):
         return opinkerfi_parser(url, retailer, baseurl, items)
    elif (retailer == 'origo'):
         return origo_parser(url, retailer, baseurl, items)
    elif (retailer == 'tolvulistinn'):
         return tolvulistinn_parser(url, retailer, baseurl, items)
    return items


def strip_number(number_string):
    return int(re.sub(r'\D', '', number_string))


def build_component(retailer, url, name, sku, price):
    return {
        'retailer': retailer, 
        'url': url,
        'name': name,
        'sku': sku.upper(),
        'price': price,
    }

def get_stripped_text(soup):
    return soup.get_text().strip()

def advania_parser(url, retailer, baseurl, items):
    response = request_session.post(url)
    data = response.json()  # Parse the JSON response

    products = data.get('products', [])  # Adjust this based on the actual JSON structure

    for product in products:
        price_info = product.get('price', {})
        discount_price_info = product.get('discount', {})
        standard_price = price_info.get('priceWithVat')  # Get the first "price" value
        special_price = discount_price_info.get('priceWithVat')
        name = product.get('name')
        sku = product.get('number')
        price = round(special_price if special_price != 0 else standard_price)
        product_url = '%s/SelectProd.action?prodId=%s' % (baseurl, product.get('id'))
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
    return items

def tolvutek_parser(category_id, retailer, baseurl, items):
    page_number = 0
    while (page_number < 10):
        page_number += 1
        response = request_session.post('https://tolvutek.is/api/FetchProducts?categoryId=847', verify=True)

        products = response.json().get('currentProducts')
        if (len(products) == 0):
            break
        for product in products:
            standard_price = product.get('priceIncTax')
            special_price = product.get('specialPriceIncTax')
            name = product.get('name')
            sku = product.get('sku')
            price = round(special_price if special_price is not None else standard_price)
            product_url = '%s/SelectProd.action?prodId=%s' % (baseurl, product.get('id'))
            items.append(build_component(retailer, product_url, name, sku, price))
            print(items[-1])
    return items

def elko_parser(url, retailer, baseurl, items):
    page = 1
    while True:
        paginated_url = f"{url}?page={page}"
        response = requests.get(paginated_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the script tag containing the JSON data
        script_tag = soup.find('script', type='application/json')

        if script_tag:
            print(f"Script tag found on page {page}")
            try:
                # Extract the JSON data from the script tag
                data = json.loads(script_tag.string)

                # Dig deeper into the props to find initialData
                props = data.get('props', {})
                pageProps = props.get('pageProps', {})
                products = pageProps.get('initialData', {}).get('hits', [])

                if not products:
                    print(f"No products found on page {page}")
                    break

                for product in products:
                    name = product.get('name')
                    sku = product.get('sku')
                    price_info = product.get('listings', {}).get('webshop', {}).get('price', {})
                   # print("price:", price_info)  # Debugging line to check the price structure
                    price = price_info.get('price')
                    product_url = '%s/%s' % (baseurl, product.get('product', {}).get('slug'))
                    items.append(build_component(retailer, product_url, name, sku, price))
                    print(items[-1])

                page += 1  # Move to the next page
            except json.JSONDecodeError:
                print("Error decoding JSON data")
                break
        else:
            print(f"Script tag not found on page {page}")
            break

    return items

def computer_parser(url, retailer, baseurl, items):
    page_number = 0
    while (page_number < 10):
        page_number += 1
        page_url = '%s?page=%s&ajax=1' % (url, page_number,)
        print('page-url', page_url)
        page = request_session.get(page_url)
        soup = BeautifulSoup(page.text, 'html5lib')
        products = soup.find_all('div', class_='product-item')
        if (len(products) == 0):
            break
        for product in products:
            name = get_stripped_text(product.find('h3', class_='product-title'))
            price = strip_number(product.find('span', class_='product-price').find('a', class_='black').get_text())
            product_url = baseurl + product.find('a').get('href')
            sku = ''
            items.append(build_component(retailer, product_url, name, sku, price))
            print(items[-1])
    return items

def kisildalur_parser(category_id, retailer, baseurl, items):
    url = 'https://kisildalur.is/api/categories/%s?includes=public_products&fields=public_products(id,price,properties,name,productid)' % (category_id,)
    response = request_session.get(url)
    products = response.json().get('public_products')
    for product in products:
        name = product.get('name')
        price = product.get('price')
        product_url = '%s/category/%s/products/%s' % (baseurl, category_id, product.get('id'))
        sku = product.get('productid')
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
    return items

def macland_parser(url, retailer, baseurl, items):
    page = request_session.get(url)
    soup = BeautifulSoup(page.text, 'html5lib')
    products = soup.find_all('li', class_='product')

    for product in products:
        sku = product.find('span', class_='gtm4wp_productdata').get('data-gtm4wp_product_id').replace('SKU-', '')
        name = get_stripped_text(product.find('h2', class_='woocommerce-loop-product__title'))
        price = strip_number(product.find('span', class_='amount').get_text())
        product_url = product.find('a').get('href')
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
    return items

def opinkerfi_parser(url, retailer, baseurl, items):
    page = request_session.get(url)
    soup = BeautifulSoup(page.text, 'html5lib')
    
    # Find the script tag containing the product data
    script_tag = soup.find('script', text=re.compile(r'gtag\("event", "view_item_list"'))
    if script_tag:
        # Extract the JSON data from the script tag
        json_match = re.search(r'items: (\[.*?\])', script_tag.string, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
            #print("Extracted JSON text:", json_text)  # Debugging line to check the extracted JSON

            # Convert the JSON text to a valid JSON format
            json_text = re.sub(r'(\w+):', r'"\1":', json_text)  # Add double quotes around property names
            json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas before closing brackets
            #print("Formatted JSON text:", json_text)  # Debugging line to check the formatted JSON

            try:
                products = json.loads(json_text)
                for product in products:
                    sku = product.get('item_id')
                    name = product.get('item_name')
                    price = round(product.get('price'))

                    # Find the <a> tag with the href attribute containing the product name
                    product_tag = soup.find('a', href=re.compile(name.replace(' ', '-').lower()))
                    #print("Product tag:", product_tag)  # Debugging line to check the product tag
                    if product_tag:
                        product_url = baseurl + product_tag['href']
                    else:
                        product_url = baseurl + '/product/' + sku

                    items.append(build_component(retailer, product_url, name, sku, price))
                    print(items[-1])
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                # Print the part of the JSON that caused the error
                error_position = e.pos
                print("Error at position:", error_position)
                print("Problematic JSON part:", json_text[error_position-50:error_position+50])
        else:
            print("No JSON data found in script tag.")
    else:
        print("No product data found in script tag.")
    
    return items

def tolvulistinn_parser(url, retailer, baseurl, items):
    page_number = 0
    while (page_number < 10):
        page_number += 1
        page_url = '%s?page=%s&ajax=1' % (url, page_number,)
        print('page-url', page_url)
        page = request_session.get(page_url)
        soup = BeautifulSoup(page.text, 'html5lib')
        products = soup.find_all('div', class_='productItem')
        if (len(products) == 0):
            break
        for product in products:
            name = get_stripped_text(product.find('div', class_='productItem-title'))
            sku = get_stripped_text(product.find('div', class_='productItem-brand'))
            try:
                price = strip_number(product.find('button', class_='btn-cart').string)
            except ValueError:
                continue
            product_url = baseurl + product.find('a').get('href')
            items.append(build_component(retailer, product_url, name, sku, price))
            print(items[-1])
    return items

def origo_parser(category_id, retailer, baseurl, items):
    page_number = 0
    while (page_number < 10):
        page_number += 1
        body = {
            "action": "1",
            "id": str(category_id),
            "manus": [],
            "page": 1,
            "pageSize": 200                                                                              
        }                                                                                                 
        response = request_session.post('https://api-verslun.origo.is/FetchProducts?categoryId=847', json=body)
        # Check if the response is successful
        if response.status_code != 200:                                            
            print(f"Failed to fetch products: {response.status_code}")
            break                          
        try:                                         
            products = response.json().get('currentProducts')  
        except requests.exceptions.JSONDecodeError as e:                                                    
            print(f"JSON decode error: {e}")                                                                     
            print(f"Response text: {response.text}")                                             
            break
        if (len(products) == 0):
            break
        for product in products:
            standard_price = product.get('priceIncTax')
            special_price = product.get('specialPriceIncTax')
            name = product.get('name')
            sku = product.get('sku')
            # Ensure price is not None before rounding
            if special_price is not None:
                price = round(special_price)
            elif standard_price is not None:
                price = round(standard_price)
            else:
                price = None  # or handle this case as needed
            
            product_url = '%s/SelectProd.action?prodId=%s' % (baseurl, product.get('id'))
            items.append(build_component(retailer, product_url, name, sku, price))
            print(items[-1])
        return items
