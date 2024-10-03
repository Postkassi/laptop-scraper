import argparse
from retailers import retailer_urls
from page_parsers import extract_items_from_url
from server import upload_to_server

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scrape retailer data.')
    parser.add_argument('action', nargs='?', default='scrape', choices=['scrape', 'list'], help='Action to perform: scrape or list')
    parser.add_argument('retailer_index', nargs='?', type=int, help='Index of the retailer to scrape')
    return parser.parse_args()

def list_retailers():
    print("Available retailers to scrape:")
    for index, retailer in enumerate(retailer_urls.keys()):
        print(f"{index}: {retailer}")

def main():
    args = parse_arguments()

    if args.action == 'list':
        list_retailers()
        return

    items = []

    if args.retailer_index is not None:
        # Scrape only the specified retailer
        retailer = list(retailer_urls.keys())[args.retailer_index]
        print(f'Start scraping of {retailer}')
        urls = retailer_urls[retailer]['urls']
        for url in urls:
            items += extract_items_from_url(url, retailer)
    else:
        # Scrape all retailers
        for retailer in retailer_urls:
            print(f'Start scraping of {retailer}')
            urls = retailer_urls[retailer]['urls']
            for url in urls:
                items += extract_items_from_url(url, retailer)

    print('Total items:', len(items))
#    upload_to_server(items)

if __name__ == '__main__':
    main()

