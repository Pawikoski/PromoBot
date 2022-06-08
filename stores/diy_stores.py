import requests
import json
import time
import random
import re

from base64 import urlsafe_b64encode
from bs4 import BeautifulSoup
from operations.database import add_products, check_product


class Scraper:
    def __init__(self, store, category_name, category_url, products):
        self.products_in_db = products
        self.store = store
        self.category_name = category_name
        self.category_url = category_url

    def rtveuroagd(self):
        soup = BeautifulSoup(requests.get(self.category_url).text, 'lxml')
        try:
            pages = int(soup.findAll("a", {"class": "paging-number"})[-1].text)
        except ValueError:
            return False

        for page in range(pages):
            new_products = []
            page += 1
            print(f"RTV Euro AGD ({self.category_name}), page: {page}")
            url = self.category_url.replace(".bhtml", f",strona-{page}.bhtml")

            soup = BeautifulSoup(requests.get(url).text, 'lxml')
            products_raw = soup.findAll("div", {"class": "product-row"})

            for product in products_raw:
                name_and_url = product.find("a", {"class": "js-save-keyword"})
                name = name_and_url.text.strip()
                url = 'https://www.euro.com.pl' + name_and_url['href']
                try:
                    img_url = "https:" + product.find("div", {"class": "product-photo"}).find("img")['data-original']
                except KeyError:
                    img_src = product.find("div", {"class": "product-photo"}).find("img")['src']
                    if img_src[1] == "/":
                        img_url = "https:" + img_src
                    else:
                        img_url = "https://www.euro.com.pl" + img_src

                availability = True
                if not product.find("button", {"class": "add-to-cart"}):
                    availability = False
                    price = None
                else:
                    price = float(product.find("div", {"class": "selenium-price-normal"}).text.strip().replace("zł", "")
                                  .replace(" ", "").replace(",", ".").replace("\xa0", ""))

                result = check_product(name, url, price, availability, self.products_in_db, "RTV Euro AGD",
                                       self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))
