import requests
import os


def search_best_price_db(product_name, store_name, category_name):
    request_data = {'product_name': product_name, 'store_name': store_name, 'category_name': category_name}
    best_price = requests.get(f'{os.environ.get("API_URL")}search-best-price', json=request_data)

    return best_price


if __name__ == "__main__":
    price = search_best_price_db('procesor amd ryzen 5 3600', 'Morele', 'CPUs').json()['lowest_price']
    print(price)
