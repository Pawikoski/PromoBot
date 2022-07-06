import random

import requests
from stores.popular import Scraper

import time
import traceback

import concurrent.futures
import os


API_URL = "http://127.0.0.1:8000/promobot/"
API_KEY = os.environ.get("API_KEY")

api_headers = {
    "Authorization": f"Token {API_KEY}"
}


def work_on_products(store, category_name, category_url, products):
    try:
        print(category_url)
        scraper = Scraper(store=store, category_name=category_name, category_url=category_url, products=products)

        match store:
            # case "RTV Euro AGD":
            #     scraper.rtveuroagd()
            # case "Media Expert": TODO:
            #     scraper.mediaexpert()
            # case "Neonet":
            #     scraper.neonet()
            # case "Avans": TODO:
            #     scraper.avans()
            # case "x-kom":
            #     scraper.x_kom()
            # case "Komputronik": TODO:
            #     scraper.komputronik()
            # case "Morele": # TODO: sometimes already existing url
            #     scraper.morele()
            # case "Sferis":# TODO: sometimes already existing url
            #     scraper.sferis()
            case "OleOle":
                scraper.oleole()

    except Exception:
        print(category_url, store, "\n\n\n", traceback.print_exc())
        time.sleep(15)


def collect_data():
    print("log: starting. collecting data")
    collected_data = []
    stores = requests.get(API_URL + 'stores', headers=api_headers).json()
    for store in stores:
        # if store['name'] != "Neonet":
        #     continue
        try:
            categories = requests.get(API_URL + f'categories/{store["id"]}').json()
        except TypeError:
            print("You need to provide valid API key")
            return False
        for category in categories:
            data = requests.get(API_URL + f'category-details/{store["id"]}/{category["id"]}').json()
            print("log, category, store, data")
            collected_data.append((store, category, data))

    random.shuffle(collected_data)
    return collected_data


def process_data(data):
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for record in data:
            store = record[0]['name']
            category_name = record[1]["name"]
            category_url = record[2]["category_url"]
            products = record[2]['products']

            executor.submit(work_on_products, store, category_name, category_url, products)
            # time.sleep(random.uniform(0.5, 3.0))


def main():
    while True:
        _data = collect_data()
        if not _data:
            break
        process_data(_data)
        print("okrążenie numero uno")
        time.sleep(3600)


if __name__ == "__main__":
    main()


