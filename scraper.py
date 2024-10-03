from retailers import retailer_urls
from page_parsers import extract_items_from_url

from server import upload_to_server


items = []
for retailer in retailer_urls:
    print('Start scraping of %s' % (retailer,))
    urls = retailer_urls.get(retailer).get('urls')
    for url in urls:
        items = items + extract_items_from_url(url, retailer)


print('total items', len(items))
upload_to_server(items)
