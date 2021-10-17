import re
import requests
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
    elif (retailer == 'att'):
       return att_parser(url, retailer, baseurl, items)
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
    elif (retailer == 'tolvutek'):
        return tolvutek_parser(url, retailer, baseurl, items)
    return items


def strip_number(number_string):
    return int(re.sub('\D', '', number_string))


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

def att_parser(url, retailer, baseurl, items):
    pages = 1000
    page_number = 1
    products = []
    loops = 0

    while (page_number <= pages and loops < 10):
        page_url = '%s?p=%s' % (url, page_number,)
        page = request_session.get(page_url)
        soup = BeautifulSoup(page.text, 'html5lib')
        if pages == 1000:
            try:
                pages = strip_number(soup.find('div', class_='pages').find_all('a', class_='page')[-1].get_text())
            except:
                pages = 1
        print('page-url', page_url)
        products = products + soup.find_all('li', class_='product-item')
        page_number += 1
        loops += 1

    for product in products:
        name = get_stripped_text(product.find('a', class_='product-item-link'))
        price = strip_number(product.find('span', class_='price-wrapper').get_text())
        product_url = product.find('a', class_='product-item-link').get('href')
        sku = get_stripped_text(product.find('dvi', class_='product-item-sku'))
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
    return items

def advania_parser(url, retailer, baseurl, items):
    page = request_session.get(url)
    soup = BeautifulSoup(page.text, 'html5lib')
    products = soup.find_all('div', class_='productBoxContainer')

    for product in products:
        info = product.find('div', class_='info-wrapper')
        sku = get_stripped_text(info.find('p', class_='productNumber'))
        name = get_stripped_text(info.find('p', class_='title'))
        price = strip_number(product.find('span', class_='priceAmount').get_text())
        product_url = baseurl + product.find('a').get('href')
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
    return items

def elko_parser(url, retailer, baseurl, items):
    pages = 1000
    page_number = 1
    products = []
    loops = 0

    while (page_number <= pages and loops < 10):
        page_url = '%s?p=%s' % (url, page_number,)
        page = request_session.get(page_url)
        soup = BeautifulSoup(page.text, 'html5lib')
        if pages == 1000:
            try:
                pages = strip_number(soup.find_all('', class_='page-item')[-2].get_text())
            except:
                pages = 1
        print('page-url', page_url)
        products = products + soup.find_all('div', class_='product-item-info')
        page_number += 1
        loops += 1

    for product in products:
        name = get_stripped_text(product.find('h4', class_='product-name'))
        price = strip_number(product.find('span', class_='price-tag').get_text())
        product_url = product.find('a', class_='price-button').get('href')
        sku = get_stripped_text(product.find('div', class_='product-code'))
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
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
    products = soup.find_all('div', class_='product')

    for product in products:
        sku = product.find('p', class_='vnr-font').get_text().strip().split(' ')[1]
        name = get_stripped_text(product.find('h3', class_='nomargins'))
        price = strip_number(product.find('span', class_='price').get_text())
        product_url = baseurl + product.find('a', class_='bluetext').get('href')
        items.append(build_component(retailer, product_url, name, sku, price))
        print(items[-1])
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
            "page": 1
        }
        response = request_session.post('https://verslun.origo.is/FetchProducts', json=body)
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

def tolvutek_parser(category_id, retailer, baseurl, items):
    page_number = 0
    while (page_number < 10):
        page_number += 1
        body = {
            'action': 1,
            'page': page_number,
            'manus': [],
            'id': str(category_id),
        }
        response = request_session.post('https://tolvutek.is/FetchProducts', verify=False, json=body)
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
