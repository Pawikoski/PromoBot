import requests
from .product import clear_product_name
from .ceneo import search_ceneo


def add_products(data):
    requests.post('http://127.0.0.1:8000/promobot/products/', json=data)
    print(f"{data['store_name']}, {len(data['products'])} new products ({data['store_category']})")


def update_product(product_id, product: dict):
    """
    :param product_id:
    :param product:
    :return:
    """
    response = requests.put(
        url=f'http://127.0.0.1:8000/promobot/products/{product_id}',
        json={"product_to_update": product}
    )
    return response


def add_product_to_promo(product_url: str, store: str, category: str, certain: bool) -> bool:
    """
    :param product_url:
    :param store:
    :param category:
    :param certain:
    :return: boolean value: True (success) or False (fail)
    """

    data = {
        "url": product_url,
        "store_name": store,
        "category_name": category,
        "certain": certain
    }

    response = requests.post(f'http://127.0.0.1:8000/add-product-to-promo/', json=data)
    if response.status_code == 200:
        return True
    return False


def check_product(name, url, price, availability, products_in_db: dict, store: str, category: str):
    products_url_and_prices = {}
    for product in products_in_db:
        products_url_and_prices[product['url']] = {"price": product['price'], "id": product['id']}

    if url not in products_url_and_prices.keys():
        return {
            "new": {
                "url": url,
                "name": name,
                "price": price,
                "available": availability
            }
        }
    elif url in products_url_and_prices.keys():
        price_in_db = products_url_and_prices[url]['price']
        if price_in_db:
            price_in_db = float(price_in_db)
        if price:
            price = float(price)
        if price != price_in_db:
            r = update_product(products_url_and_prices[url]['id'], {
                    "url": url,
                    "name": name,
                    "price": price,
                    "available": availability
                })
            if availability and "last_best_price" in r.json():
                print("best price")
                price = float(price)
                if price < price_in_db and (1 - price/price_in_db) * 100 > 16.0:
                    print("very low price")
                    print(f"price: {price}, price in db: {price_in_db}")

                    clean_name = clear_product_name(name, store_name=store, category_name=category)
                    if not clean_name:
                        print("NO NAME!!!", name, store, category)
                        clean_name = name

                    # TODO: endpoint - search-best-price
                    response = requests.get(f'', json={
                        "product_name": clean_name,
                        "category_name": category
                    })

                    lowest_price_all_stores = float(response.json()['lowest_price'])
                    if price <= lowest_price_all_stores:
                        print("LOG: CENEO CHECKin")
                        lowest_from_ceneo = search_ceneo(name)
                        if lowest_from_ceneo and price < lowest_from_ceneo \
                                and (1 - price/lowest_from_ceneo) * 100 > 15.0:
                            add_product_to_promo(product_url=url, store=store, category=category, certain=True)
                        elif not lowest_from_ceneo:
                            print("NOT CERTAIN HERE")
                            add_product_to_promo(product_url=url, store=store, category=category, certain=False)

            if r.status_code == 200:
                print(f"UPDATED: {name}, {price}, {url}")
                return {"success": "product updated"}
            else:
                return {"error": "product not updated!"}
        return {"status": "same price"}
