import requests
import json
import time
import random
import re

from base64 import urlsafe_b64encode
from bs4 import BeautifulSoup
from operations.database import add_products, check_product
from tqdm import tqdm


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

                result = check_product(name, url, price, availability, self.products_in_db, "RTV Euro AGD", self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))

    def mediaexpert(self):
        def get_soup(page_number: int = 1):
            s = None
            while not s:
                try:
                    session = requests.Session()
                    session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"

                    payload = {"limit": 70, "page": page_number}
                    response = session.get(url=self.category_url, params=payload, allow_redirects=True, timeout=10)
                    s = BeautifulSoup(response.text, 'lxml')
                    [x.extract() for x in s.findAll("script")]

                    if not s:
                        time.sleep(3)
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
        except AttributeError:
            pages = 1
        except ValueError:
            return False

        for page in range(pages):
            new_products = []
            update_products = []
            page += 1
            print(f"Mediaexpert ({self.category_name}), page: {page}")

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

                result = check_product(name, url, price, availability, self.products_in_db, "Media Expert", self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))

    def neonet(self):
        splitted_url = self.category_url.split(".pl")[1]

        graphql_url = "https://www.neonet.pl/graphql"
        api_version = "2.125.0"

        def get_category_id():
            _payload = {
                "query": 'query resolveUrl($urlKey: String!, $search: String) { urlResolver(url: $urlKey, search: $search) { type id canonical_url  }}',
                "variables": '{"urlKey":"' + splitted_url + '","search":""}',
                "v": api_version
            }
            r = requests.get(graphql_url, params=_payload).json()['data']['urlResolver']
            if r['canonical_url'] != self.category_url:
                return False
            return r['id']

        category_id = str(get_category_id())
        if not category_id:
            print("Cant get category id sorrry memory")
            return

        def get_products_ids():
            _payload = {
                "query": 'query productsForCategory($id: String!, $ids: [Int], $attributes: [String], $sortBy: String, $sortOrder: String) { products: msProducts(filter: {category_id: {eq: $id}, attributes: $attributes}, facet: true, sort: {sort_by: $sortBy, sort_order: $sortOrder}) { total_count items_ids facets { code values { value_id count } } stats { code values { min max count } } } categories: msCategories(ids: $ids) { items { id adserver_ids(version: 2) { banner_category { graphics_id } wallpaper { graphics_id } floater { graphics_id } banner_listing { graphics_id } } } }}',
                "variables": '{"attributes":[],"sortOrder":"DESC","sortBy":"popularity","id":"' + category_id + '","ids":[' + category_id + ']}',
                "v": api_version
            }
            r = requests.get(graphql_url, params=_payload).json()['data']['products']
            return r['items_ids']

        ids = get_products_ids()

        divided_ids = [ids[i:i + 100] for i in range(0, len(ids), 100)]
        data = []

        for part_ids in divided_ids:
            print(f"Neonet ({self.category_name})")
            new_products = []
            payload = {
                "query": 'query msProducts( $ids: [Int] ) { products: msProducts( filter: { skus: $ids } attributes: true ) { items { sku,name,price,final_price,request_path,availability,request_path,thumbnail } } }',
                # Todo: Many more query parameters available, consider this
                "variables": '{"ids": ' + str(part_ids) + '}',
                "v": api_version
            }
            products_raw = requests.get(graphql_url, params=payload).json()['data']['products']['items']

            for product in products_raw:
                name = product['name']
                url = "https://neonet.pl" + product['request_path']
                availability = product['availability'] == 1
                img_src = product['thumbnail']

                img_data = {"bucket":"https://cdn.neonet.pl","key":f"karty/pliki/zdjecia/{img_src}","edits":{"webp":{"quality":80},"resize":{"fit":"contain","background":{"r":255,"g":255,"b":255,"alpha":1},"width":600,"height":450}}}
                b64_img_src = urlsafe_b64encode(json.dumps(img_data).encode()).decode("utf-8")
                img_url = f"https://cdn-img.neonet.pl/{b64_img_src}"

                price = None
                if availability:
                    price = product['final_price']

                result = check_product(name, url, price, availability, self.products_in_db, "Neonet", self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))

    def avans(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        payload = {
            "limit": 50,
        }
        response = requests.get(self.category_url, params=payload,
                                headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            pages = int(soup.find("form", {"name": "paginate-form"}).find("span", {"class": "is-total"}).text.strip())
        except AttributeError:
            pages = 1
        except ValueError:
            return False

        for page in range(pages):
            new_products = []
            page += 1
            print(f"Avans ({self.category_name}), page: {page}")

            p = {
                "limit": 50,
                "page": page
            }

            response = requests.get(self.category_url, params=p, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            container = soup.find("div", {"class": "c-grid"})
            products_raw = container.findAll("div", {"data-zone": "OFFERBOX"})
            for product in products_raw:
                try:
                    product_data = dict(
                        json.loads(product.find("meta", {'data-analytics-item': True})['data-analytics-item']))
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

                result = check_product(name, url, price, availability, self.products_in_db, "Avans", self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))

    def x_kom(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        response = requests.get(self.category_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        pagination = soup.find("input", {"type": "number", "value": "1"})
        if not pagination:
            return False

        pages = int(pagination['max'])

        for page in range(pages):
            new_products = []
            page += 1
            print(f"x-kom ({self.category_name}), page: {page}")

            params = {
                "page": page,
            }

            response = requests.get(self.category_url, params=params, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            container = soup.find("div", {"id": "listing-container"})
            products_raw = container.findAll("div", {"width": True})

            for product in products_raw:
                name = product.find("h3", {"title": True}).text
                url = "https://x-kom.pl" + product.find("a")['href']
                img_url = product.findAll("img")[1]['src']

                availability = True
                if not product.find("button", {"title": "Dodaj do koszyka"}):
                    availability = False
                    price = None
                price = product.findAll("span", string=re.compile(r"^[\d ]*,\d{1,2} zł"))[-1].text. \
                    replace(" ", "").replace("zł", "").replace(",", ".")

                result = check_product(name, url, price, availability, self.products_in_db, "x-kom", self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

            time.sleep(random.uniform(0.2, 5.0))

    def komputronik(self):
        def analyze_products(raw_data):
            new_products = []
            for product in tqdm(raw_data, desc=f"Komputronik: Analyzing {len(raw_data)} products"):
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

                if product.find("ktr-product-availability")['is-buyable'] == "0":
                    price = None
                    availability = False
                else:
                    availability = True
                    # TODO: Catch exceptions for price:
                    price = float(str(product.find("span", {"class": "price"}).text).encode("ascii", "ignore").decode()
                                  .strip().replace(" ", "").replace("zł", "").replace("z", "").replace(",", "."))

                result = check_product(name, url, price, availability, self.products_in_db, "Komputronik",
                                       self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }

        response = requests.get(self.category_url, headers=headers)
        if response.status_code == 408:
            print("Komputronik 408")
            time.sleep(5)
            response = requests.get(self.category_url, headers=headers)
        if response.status_code != 200:
            print("Komputronik error")
            return False

        soup = BeautifulSoup(
            response.text, 'lxml'
        )

        try:
            pages_raw = soup.find_all("a", href=re.compile(r'\?p=\d{1,3}'))
            if len(pages_raw) == 2:
                pages = 2
            else:
                pages = int(pages_raw[-2].text)
        except (ValueError, AttributeError, TypeError, IndexError):
            pages = 1

        try:
            print(f"Komputronik ({self.category_name}), page: 1")
            analyze_products(soup.findAll("li", {"class": "product-entry2"}))
        except AttributeError:
            print("log: no products komputronik")
            return False

        if pages > 1:
            for page in range(2, pages + 1):
                print(f"Komputronik ({self.category_name}), page: {page}")

                response = requests.get(self.category_url, params={"p": page}, headers=headers)
                if response.status_code != 200:
                    time.sleep(20)
                    response = requests.get(self.category_url, params={"p": page}, headers=headers)

                soup = BeautifulSoup(
                    response.text, 'lxml'
                )
                analyze_products(soup.findAll("li", {"class": "product-entry2"}))
                time.sleep(random.uniform(1.0, 8.0))

    def morele(self):
        def analyze_products(raw_data):
            new_products = []
            for product in tqdm(raw_data, desc=f"Morele: Analyzing {len(raw_data)} products"):
                name = product['data-product-name']
                new_url = "https://morele.net" + product.find("a", {"class": "productLink"})['href']
                try:
                    img_url = product.find("img", {"class": "product-image"})['src']
                except KeyError:
                    img_url = product.find("img", {"class": "product-image"})['data-src']
                except TypeError:
                    img_url = None

                if not product.find("a", href=re.compile(fr"/basket/add/{product['data-product-id']}")):
                    availability = False
                    price = None
                else:
                    availability = True
                    price = float(product['data-product-price'])  # todo: catch AttributeError exceptions

                result = check_product(name, new_url, price, availability, self.products_in_db, "Morele",
                                       self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }

        soup = BeautifulSoup(requests.get(self.category_url, headers=headers).text, 'lxml')

        try:
            pages = int(soup.find("input", {"type": "number", "data-pagination-href": True})["data-max-page"])
        except TypeError:
            pages = int(soup.findAll("div", {"data-page": True})[-1]['data-page'])
        except AttributeError:
            pages = 1

        try:
            print(f"Morele ({self.category_name}), page: 1")
            products_raw = soup.find_all("div", {"class": "cat-product"})
            analyze_products(products_raw)
        except AttributeError:
            print("log: no products morele")
            return False

        if pages > 1:
            for page in range(2, pages + 1):
                print(f"Morele ({self.category_name}), page: {page}")
                url = self.category_url + f",,,,,,,,0,,,,/{page}/"
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    time.sleep(20)
                    response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                products_raw = soup.findAll("div", {"class": "cat-product"})
                analyze_products(products_raw)
                time.sleep(random.uniform(0.2, 5.0))

    def sferis(self):
        def analyze_products(raw_data):
            new_products = []
            for product in tqdm(raw_data, desc=f"Sferis: Analyzing {len(raw_data)} products"):
                name = product.find("p", {"class": "title"}).text
                url = "https://sferis.pl" + product.a['href']
                img_url = "https://sferis.pl" + product.find("picture").find("source", {"type": "image/jpeg"})['srcset']

                if not product.find("button", {"title": "Dodaj do koszyka"}):
                    availability = False
                    price = None
                else:
                    availability = True
                    price = float(
                        product.find("span", {"class": "price"}).text.replace(",", ".").replace("zł", "").replace(" ",
                                                                                                                  "")
                    )

                result = check_product(name, url, price, availability, self.products_in_db, "Sferis",
                                       self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products({"store_name": self.store, "store_category": self.category_name, "products": new_products})

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        soup = BeautifulSoup(requests.get(self.category_url, headers=headers, params={"l": 150}).text, 'lxml')

        try:
            pages = int(soup.find("span", {"data-pages": True})['data-pages'])
        except (ValueError, AttributeError, TypeError):
            pages = 1

        try:
            print(f"Sferis ({self.category_name}), page: 1")
            analyze_products(
                soup.find("article", {"id": "jsProductListingItems"}).find_all("div", {"class": "jsSwipe"})
            )
        except AttributeError:
            print("log: no products sferis")
            return False

        if pages > 1:
            for page in range(2, pages + 1):
                print(f"Sferis ({self.category_name}), page: {page}")
                soup = BeautifulSoup(
                    requests.get(self.category_url, params={"l": 150, "p": page}, headers=headers).text, 'lxml'
                )
                analyze_products(
                    soup.find("article", {"id": "jsProductListingItems"}).find_all("div", {"class": "jsSwipe"})
                )
                time.sleep(random.uniform(0.2, 5.0))

    def oleole(self):
        def analyze_products(raw_data):
            new_products = []
            for product in tqdm(raw_data, desc=f"OleOle: Analyzing {len(raw_data)} products"):
                name_and_url = product.find("h2", {"class": "product-name"})
                name = name_and_url.text.strip()
                product_url = "https://oleole.pl" + name_and_url.a['href']
                img_url = "https:" + product.find("div", {"class": "product-photo"}).find("img")['data-original']

                if not product.find("button", {"class": "add-to-cart"}) or "disabled" in product.find("button", {
                    "class": "add-to-cart"}).attrs.keys():
                    availability = False
                    price = None
                else:
                    availability = True
                    price_tag = product.find("div", {"class": "selenium-price-normal"})
                    price = float(
                        str(price_tag.text).encode("ascii", "ignore").decode().strip().replace(" ", "").
                            replace("zł", "").replace("z", "").replace(",", "."))

                result = check_product(name, product_url, price, availability, self.products_in_db, "OleOle",
                                       self.category_name)
                if 'new' in result.keys():
                    r = result['new']
                    r['img'] = img_url
                    new_products.append(r)

            if new_products:
                add_products(
                    {"store_name": self.store, "store_category": self.category_name, "products": new_products})

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }

        soup = BeautifulSoup(requests.get(self.category_url, headers=headers).text, 'lxml')

        try:
            pages = int(soup.findAll("a", {"class": "paging-number"})[-1].text)
        except AttributeError:
            pages = 1

        try:
            print(f"OleOle ({self.category_name}), page: 1")
            analyze_products(
                soup.find("div", {"id": "product-list"}).findAll("div", {"class": "product-for-list"})
            )
        except AttributeError:
            print("log: no products oleole")
            return False

        if pages > 1:
            for page in range(2, pages + 1):
                print(f"OleOle ({self.category_name}), page: {page}")
                url = self.category_url.replace(".bhtml", f",strona-{page}.bhtml")
                soup = BeautifulSoup(requests.get(url, headers=headers).text, 'lxml')

                analyze_products(
                    soup.find("div", {"id": "product-list"}).findAll("div", {"class": "product-for-list"})
                )
                time.sleep(random.uniform(0.2, 5.0))



