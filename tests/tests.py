import os

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
}


def mediaexpert():
    def get_soup(page_number: int = 1):
        s = None
        while not s:
            try:
                cat_url = "https://www.mediaexpert.pl/komputery-i-tablety/laptopy-i-ultrabooki/laptopy"
                session = HTMLSession()
                headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

                payload = {"limit": 70, "page": page_number}
                response = session.get(url=cat_url, headers=headers, params=payload)
                response.html.render(sleep=10)
                print(response)
                s = BeautifulSoup(response.html.raw_html, 'lxml')
                [x.extract() for x in s.findAll("script")]

                if not s:
                    time.sleep(3)
                    raise AttributeError
                else:
                    return s
            except (requests.exceptions.ReadTimeout, AttributeError):
                time.sleep(random.randint(3, 12))
                response = response.html.render()
                get_soup(page_number)

    soup = get_soup()

    try:
        pages_tag = soup.find("div", {"class": "pagination"}).find("span", {"class": "from"})
        pages_tag.small.decompose()
        pages = int(pages_tag.text)
    except AttributeError:
        pages = 1
    except ValueError:
        print("asdfasd")
        return False

    for page in range(pages):
        new_products = []
        update_products = []
        page += 1
        print(f"Mediaexpert (test), page: {page}")

        soup = get_soup(page)

        products_raw = soup.findAll("div", {"class": "offer-box"})

        for product in products_raw:
            name_and_url = product.find("h2", {"class": "name"}).a
            name = name_and_url.text.strip()
            url = "https://mediaexpert.pl" + name_and_url['href']
            img_url = None

            availability = True
            if not product.find("button", {"class": "add-to-cart"}):
                availability = False
                price = None
            else:
                price_tag = product.find("div", {"class": "main-price"})
                whole = price_tag.find("span", {"class": "whole"}).text
                rest = price_tag.find("div", {"class": "rest"}).find("span", {"class": "cents"}).text.replace(" ", "")
                price = float(f"{whole}.{rest}".encode("ascii", "ignore"))

            print(name, price, availability, url)


# TODO: Repair
def komputronik():
    response = requests.get("https://www.komputronik.pl/category/1251/monitory.html", headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        pages = int(soup.findAll("a", href=re.compile(r'\?p=\d{1,3}'))[-3].text)
    except ValueError:
        return False

    for page in range(pages):
        new_products = []
        page += 1

        params = {
            "p": page,
        }

        response = requests.get("https://www.komputronik.pl/category/1251/monitory.html", params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        products_raw = soup.findAll("li", {"class": "product-entry2"})

        for product in products_raw:
            name = product.find("div", {"class": "pe2-head"}).a.text.strip()

            img_and_url = product.find("a", {"class": "pe2-img"})

            url = None
            try:
                url = img_and_url['href']
                img_url = img_and_url.img['src']
                if 'spinner.gif' in img_url:
                    raise KeyError
            except KeyError:
                try:
                    img_url = img_and_url.img['data-original']
                except KeyError:
                    continue

            if not url:
                continue

            availability = True
            if product.find("ktr-product-availability")['is-buyable'] == "0":
                price = None
                availability = False
            else:
                price = float(str(product.find("span", {"class": "price"}).text).encode("ascii", "ignore").decode()
                              .strip().replace(" ", "").replace("zł", "").replace("z", "").replace(",", "."))

            print(name, price, url, availability, img_url)


# TODO
def obi():
    category_url = "https://www.obi.pl/technika/elektronarzedzia/c/3088"

    response = requests.get(category_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    container = soup.find("ul", {"class": "products-wp"})

    pages = 0
    try:
        pages_raw = soup.find("a", {"data-class": "pagination-links"}).text.split()
        if "Strona" in pages_raw and "z" in pages_raw:
            pages = int(pages_raw[-1])
    except AttributeError:
        return False

    for page in range(pages):
        new_products = []
        page += 1
        params = {
            "page": page
        }

        response = requests.get(category_url, headers=headers, params=params)
        soup = BeautifulSoup(response.text, 'lxml')

        container = soup.find("div", {"id": "ShopContent"}).find("ul", {"class": "products-wp"})

        products_raw = container.findAll("li", {"class": "product"})
        print(len(products_raw))
        for product in products_raw:
            info = product.find("span", {"class": "info-container"})
            name = info.find("span", {"class": "description"}).find("p").text
            url = "https://www.obi.pl" + product.a['href']

            img = product.find("span", {"class": "image-container"}).find("img")
            try:
                img_url = img['data-src']
            except KeyError:
                img_url = None

            print(name, url, img_url)
    #
    #         if not product.find("button", {"class": "add-to-cart"}) or "disabled" in product.find("button", {"class": "add-to-cart"}).attrs.keys():
    #             availability = False
    #             price = None
    #         else:
    #             availability = True
    #             price_tag = product.find("div", {"class": "selenium-price-normal"})
    #             price = float(str(price_tag.text).encode("ascii", "ignore").decode().strip().replace(" ", "").replace("zł", "").replace("z", "").replace(",", "."))
    #
    #         print(name, price, url, availability, img_url)


# TODO
def centrum_rowerowe():
    pass


# TODO
def mall():
    pass


# TODO
def intersport():
    pass


# TODO
def kfd():
    pass


# TODO
def zalando():
    pass


# TODO
def eurorower():
    pass


# TODO
def krsystem():
    pass


# TODO
def proshop():
    pass


# TODO
def alo():
    pass


# TODO
def beststore():
    pass


# TODO
def buy_it():
    pass


# TODO
def empik():
    pass


# TODO
def fatbat():
    pass


# TODO
def hanzo():
    pass


# TODO
def net_s():
    pass


# TODO
def zadowolenie():
    pass


# TODO
def whitemarket():
    pass


if __name__ == "__main__":
    mediaexpert()
