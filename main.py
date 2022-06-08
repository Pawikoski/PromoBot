import random

import requests
from stores.popular import Scraper

import time
import traceback

import concurrent.futures
import os


API_URL = os.environ.get('API_URL')


def work_on_products(store, category_name, category_url, products):
    try:
        print(category_url)
        scraper = Scraper(store=store, category_name=category_name, category_url=category_url, products=products)

        match store:
            case "RTV Euro AGD":
                scraper.rtveuroagd()
            case "Media Expert":
                scraper.mediaexpert()
            case "Neonet":
                scraper.neonet()
            case "Avans":
                scraper.avans()
            case "x-kom":
                scraper.x_kom()
            # case "Komputronik":
            #     scraper.komputronik()
            case "Morele":
                scraper.morele()
            case "Sferis":
                scraper.sferis()
            case "OleOle":
                scraper.oleole()

    except Exception:
        print(category_url, store, "\n\n\n", traceback.print_exc())
        time.sleep(15)


def collect_data():
    print("log: starting. collecting data")
    collected_data = []
    stores = requests.get(API_URL + 'get-stores').json()['stores']
    for store in stores:
        categories = requests.get(API_URL + f'get-categories/{store[0]}').json()['categories']
        for category in categories:
            data = requests.get(API_URL + f'get-category-url-and-products/{store[0]}/{category[0]}').json()
            print("log, category, store, data")
            collected_data.append((store, category, data))

    random.shuffle(collected_data)
    return collected_data


def process_data(data):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for record in data:
            store = record[0][1]
            category_name = record[1][1]
            category_url = record[2]["url"]
            products = record[2]['products'][store]

            executor.submit(work_on_products, store, category_name, category_url, products)
            time.sleep(random.uniform(0.5, 3.0))


def main():
    while True:
        _data = collect_data()
        process_data(_data)
        print("okrążenie numero uno")
        time.sleep(3600)


if __name__ == "__main__":
    main()


