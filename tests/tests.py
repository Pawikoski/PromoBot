from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
request_cookies = [
    "cookies",
    "LOGIN_SOURCE",
    "LOGIN_STATUS_VERIFY",
    "device_view",
    "2c3a31aa9e353b308f950a852d04ae5b",
    "PHPSESSID",
    "TRADEDOUBLER",
    "_gcl_au",
    "_ga",
    "_fbp",
    "meips",
    '_snrs_params',
    "livecall-account-9601",
    "_tt_enable_cookie",
    "_ttp",
    "pos_select",
    "G_ENABLED_IDPS",
    "fbm_1672692559688775",
    "utm",
    "LOGIN_CHANNEL",
    "LOGIN_STATUS",
    "remembered_device",
    "pageviewCount",
    "_uetvid",
    "cto_bundle",
    "__wph.17c52d5786ba71b3c986fe28233d4c7ae4bc37fe",
    "enp_wish_list_token",
    "_snrs_cid",
    "_ga_WEJ054CFRT",
    "_snrs_sb",
    "_snrs_sa",
    "_snrs_p",
    "SPARK_TEST",
]


def mediaexpert():
    url = "https://www.mediaexpert.pl/komputery-i-tablety/monitory-led"

    def get_soup(page_number: int = 1):
        try:
            session = requests.Session()
            session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"

            payload = {"limit": 70, "page": page_number}
            response = session.get(url=url, params=payload, allow_redirects=True, timeout=10)
            s = BeautifulSoup(response.text, 'lxml')
            [x.extract() for x in s.findAll("script")]

            if not s:
                raise AttributeError
            else:
                return s
        except (requests.exceptions.ReadTimeout, AttributeError):
            time.sleep(random.randint(3, 12))
            get_soup(page_number)

    soup = get_soup()

    try:
        pages_tag = soup.find("div", {"class": "pagination"}).find("span", {"class": "from"})
        pages_tag.small.decompose()
        pages = int(pages_tag.text)
    except ValueError:
        return False

    for page in range(pages):
        new_products = []
        update_products = []
        page += 1
        soup = get_soup(page)

        products_raw = soup.findAll("div", {"class": "offer-box"})
        print(len(products_raw))

        time.sleep(1)


    print(pages)


# DONE
def neonet():
    full_category_url = "https://www.neonet.pl/komputery/monitory.html"
    splitted_url = full_category_url.split(".pl")[1]
    print(splitted_url)

    graphql_url = "https://www.neonet.pl/graphql"
    api_version = "2.125.0"

    def get_category_id():
        payload = {
            "query": 'query resolveUrl($urlKey: String!, $search: String) { urlResolver(url: $urlKey, search: $search) { type id canonical_url  }}',
            "variables": '{"urlKey":"' + splitted_url + '","search":""}',
            "v": api_version
        }
        r = requests.get(graphql_url, params=payload).json()['data']['urlResolver']
        if r['canonical_url'] != full_category_url:
            return False
        return r['id']

    category_id = get_category_id()
    if not category_id:
        print("Cant get category id sorrry memory")
        return

    def get_products_ids():
        payload = {
            "query": 'query productsForCategory($id: String!, $ids: [Int], $attributes: [String], $sortBy: String, $sortOrder: String) { products: msProducts(filter: {category_id: {eq: $id}, attributes: $attributes}, facet: true, sort: {sort_by: $sortBy, sort_order: $sortOrder}) { total_count items_ids facets { code values { value_id count } } stats { code values { min max count } } } categories: msCategories(ids: $ids) { items { id adserver_ids(version: 2) { banner_category { graphics_id } wallpaper { graphics_id } floater { graphics_id } banner_listing { graphics_id } } } }}',
            "variables": '{"attributes":[],"sortOrder":"DESC","sortBy":"popularity","id":"100144","ids":[100144]}',
            "v": api_version
        }
        r = requests.get(graphql_url, params=payload).json()['data']['products']
        return r['items_ids']

    ids = get_products_ids()

    # print(ids)

    def get_products_data():
        divided_ids = [ids[i:i + 100] for i in range(0, len(ids), 100)]
        data = []

        for part_ids in divided_ids:
            new_products = []
            payload = {
                "query": 'query msProducts( $ids: [Int] ) { products: msProducts( filter: { skus: $ids } attributes: true ) { items { sku,name,price,final_price,request_path,availability,request_path } } }',
                # Todo: Many more query parameters available, consider this
                "variables": '{"ids": ' + str(part_ids) + '}',
                "v": api_version
            }
            products_raw = requests.get(graphql_url, params=payload).json()['data']['products']['items']

            for product in products_raw:
                name = product['name']
                url = "https://neonet.pl" + product['request_path']
                availability = product['availability'] == 1

                price = None
                if availability:
                    price = product['final_price']


# DONE
def x_kom():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }
    response = requests.get("https://www.x-kom.pl/g-6/c/15-monitory.html", headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    pagination = soup.find("input", {"type": "number", "value": "1"})
    if not pagination:
        return False

    pages = int(pagination['max'])

    for page in range(pages):
        new_products = []
        page += 1

        params = {
            "page": page,
        }

        response = requests.get("https://www.x-kom.pl/g-6/c/15-monitory.html", params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        container = soup.find("div", {"id": "listing-container"})
        products_raw = container.findAll("div", {"width": True})

        print(len(products_raw))
        for product in products_raw:
            name = product.find("h3", {"title": True}).text
            url = product.find("a")['href']

            availability = True
            if not product.find("button", {"title": "Dodaj do koszyka"}):
                availability = False
                price = None
            price = product.findAll("span", string=re.compile(r"^[\d ]*,\d{1,2} zł"))[-1].text.\
                replace(" ", "").replace("zł", "").replace(",", ".")

            print(name, price, url, availability)


# DONE
def komputronik():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

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


# DONE
def morele():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

    response = requests.get("https://www.morele.net/kategoria/myszki-464/", headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        pages = int(soup.find("input", {"type": "number", "data-pagination-href": True})["data-max-page"])
    except AttributeError:
        return False

    for page in range(pages):
        new_products = []
        page += 1

        url = "https://www.morele.net/kategoria/myszki-464/" + f",,,,,,,,0,,,,/{page}/"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        container = soup.find("div", {"class": "cat-list-products"})
        products_raw = soup.findAll("div", {"class": "cat-product"})

        for product in products_raw:
            name = product['data-product-name']
            url = "https://morele.net" + product.find("a", {"class": "productLink"})['href']
            try:
                img_url = product.find("img", {"class": "product-image"})['src']
            except KeyError:
                img_url = product.find("img", {"class": "product-image"})['data-src']
            availability = True
            if not product.find("a", href=re.compile(fr"/basket/add/{product['data-product-id']}")):
                availability = False
                price = None
            else:
                price = float(product['data-product-price'])

            print(name, price, url, availability, img_url)

        time.sleep(random.uniform(0.1, 4.0))


# DONE
def avans():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }
    payload = {
        "limit": 50,
    }
    response = requests.get("https://www.avans.pl/komputery-i-tablety/monitory-led", params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        pages = int(soup.find("form", {"name": "paginate-form"}).find("span", {"class": "is-total"}).text.strip())
    except ValueError:
        return False

    for page in range(pages):
        new_products = []
        page += 1

        p = {
            "limit": 50,
            "page": page
        }

        response = requests.get("https://www.avans.pl/komputery-i-tablety/monitory-led", params=p, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        container = soup.find("div", {"class": "c-grid"})
        products_raw = container.findAll("div", {"data-zone": "OFFERBOX"})
        for product in products_raw:
            try:
                product_data = dict(json.loads(product.find("meta", {'data-analytics-item': True})['data-analytics-item']))
            except TypeError:
                continue

            name = product_data['name']
            url = "https://avans.pl" + product.find("div", {"data-zone": "OFFERBOX_NAME"}).find("a")['href']
            img_url = "https://avans.pl" + product.find("div", {"data-zone": "OFFERBOX_PHOTO"}).find("img")['data-src']

            availability = True
            if not product.find("div", {"data-zone": "ADD_TO_CART_PRECART"}):
                availability = False
                price = None
            else:
                price = float(product_data['price'])

            print(name, price, url, availability, img_url)


# DONE, TESTED
def sferis():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }
    response = requests.get("https://www.sferis.pl/plyty-glowne-2894", headers=headers, params={"l": 150})
    soup = BeautifulSoup(response.text, 'lxml')

    pages = int(soup.find("span", {"data-pages": True})['data-pages'])

    for page in range(pages):
        new_products = []
        page += 1

        response = requests.get("https://www.sferis.pl/plyty-glowne-2894", params={"l": 150, "p": page}, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        products_raw = soup.find("article", {"id": "jsProductListingItems"}).findAll("div", {"class": "jsSwipe"})
        print(len(products_raw))
        for product in products_raw:
            name = product.find("p", {"class": "title"}).text
            url = "https://sferis.pl" + product.a['href']
            img_url = "https://sferis.pl" + product.find("picture").find("source", {"type": "image/jpeg"})['srcset']

            availability = True
            if not product.find("button", {"title": "Dodaj do koszyka"}):
                availability = False
                price = None
            price = float(product.find("span", {"class": "price"}).text.replace(",", ".").replace("zł", "").replace(" ", ""))

            print(name, price, url, availability, img_url)


# DONE, TESTED
def oleole():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

    response = requests.get("https://www.oleole.pl/monitory-led-i-lcd.bhtml", headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        pages = int(soup.findAll("a", {"class": "paging-number"})[-1].text)
    except AttributeError:
        return False

    print(pages)
    for page in range(pages):
        new_products = []
        pages += 1

        url = "https://www.oleole.pl/monitory-led-i-lcd.bhtml"
        if page > 1:
            url = url.replace(".bhtml", f",strona-{page}.bhtml")

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        container = soup.find("div", {"id": "product-list"})

        products_raw = container.findAll("div", {"class": "product-for-list"})
        print(len(products_raw))
        for product in products_raw:
            name_and_url = product.find("h2", {"class": "product-name"})
            name = name_and_url.text.strip()
            url = "https://oleole.pl" + name_and_url.a['href']
            img_url = "https:" + product.find("div", {"class": "product-photo"}).find("img")['data-original']

            if not product.find("button", {"class": "add-to-cart"}) or "disabled" in product.find("button", {"class": "add-to-cart"}).attrs.keys():
                availability = False
                price = None
            else:
                availability = True
                price_tag = product.find("div", {"class": "selenium-price-normal"})
                price = float(str(price_tag.text).encode("ascii", "ignore").decode().strip().replace(" ", "").replace("zł", "").replace("z", "").replace(",", "."))

            print(name, price, url, availability, img_url)


def obi():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

    response = requests.get("https://www.obi.pl/technika/elektronarzedzia/c/3088", headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    container = soup.find("ul", {"class": "products-wp"})
    print(container)

    # print(soup)
    try:
        pages_raw = soup.find("a", {"data-class": "pagination-links"}).text.split()
        if "Strona" in pages_raw and "z" in pages_raw:
            print(pages_raw[-1])
    except AttributeError:
        return False

    # print(pages)
    # for page in range(pages):
    #     new_products = []
    #     pages += 1
    #
    #     url = "https://www.oleole.pl/monitory-led-i-lcd.bhtml"
    #     if page > 1:
    #         url = url.replace(".bhtml", f",strona-{page}.bhtml")
    #
    #     response = requests.get(url, headers=headers)
    #     soup = BeautifulSoup(response.text, 'lxml')
    #
    #     container = soup.find("div", {"id": "product-list"})
    #
    #     products_raw = container.findAll("div", {"class": "product-for-list"})
    #     print(len(products_raw))
    #     for product in products_raw:
    #         name_and_url = product.find("h2", {"class": "product-name"})
    #         name = name_and_url.text.strip()
    #         url = "https://oleole.pl" + name_and_url.a['href']
    #         img_url = "https:" + product.find("div", {"class": "product-photo"}).find("img")['data-original']
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


if __name__ == "__main__":
    obi()
