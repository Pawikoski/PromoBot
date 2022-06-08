import requests
import urllib.parse

from bs4 import BeautifulSoup


def ceneo_url(search_phrase: str) -> str:
    # ceneo_categories = {
    #     "tvs": 'Sprzet_RTV',
    #     "smartbands": "Telefony_i_akcesoria",
    #     "smartwatches": "Sport_i_rekreacja",
    #     "thermal pastes": "",
    #     "pc fans": "",
    #     "cpu coolings": "",
    #     "sound cards": "",
    #     "ram": "",
    #     "cases": "",
    #     "hdd": "",
    #     "ssd": "",
    #     "headphones": "",
    #     "motherboards": "",
    #     "psus": "",
    #     "cpus": "",
    #     "gpus": "",
    #     "keyboards": "",
    #     "mouses": "",
    #     "monitors": "",
    #     "laptops": "",
    # }
    try:
        return f"https://www.ceneo.pl/;szukaj-{search_phrase}"
    except KeyError:
        print("BŁĄD KATEGORII\nBŁĄD KATEGORII\nBŁĄD KATEGORII\nBŁĄD KATEGORII\nBŁĄD KATEGORII\nBŁĄD KATEGORII")

    # TODO: KOMPUTERY??? OTHER CATEGORIES MAN
    # TODO: Match categories [] to
    #  ###ceneo categories [
    #  Biuro i firma
    #  Biżuteria i zegarki
    #  Budowa i remont
    #  Dla dziecka
    #  Dom i wnętrze
    #  Hobby i zwierzęta
    #  Komputery
    #  Księgarnia
    #  Moda
    #  Motoryzacja
    #  Ogród
    #  Sport i rekreacja
    #  Sprzęt AGD
    #  Sprzęt RTV
    #  Telefony i akcesoria
    #  Uroda
    #  Zdrowie
    #  ]###


def encode_product_name(product_name: str) -> str:
    encoded_name = product_name.lower().replace(" ", "+")
    polish_signs = 'ąćęłńżźśó'
    for sign in polish_signs:
        encoded_name = encoded_name.replace(sign, urllib.parse.quote(sign))

    special_chars = '/*'
    for char in special_chars:
        encoded_name = encoded_name.replace(char, '+')

    while True:
        if '++' in encoded_name:
            encoded_name.replace("++", "+")
        else:
            break

    return encoded_name


def search_ceneo(product_name) -> float | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

    name = encode_product_name(product_name)
    url = ceneo_url(name)
    print(url)
    response = requests.get(url=url, headers=headers)
    if response.status_code == 302:
        new_url = f"https://www.ceneo.pl/;szukaj-{name}"
        response = requests.get(url=new_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    products = soup.findAll("div", {"class": "cat-prod-row"})
    if len(products) > 1:
        print("LOG: CENEO, MORE THAN 1 RESULT")

    try:
        ceneo_name = products[0]['data-productname']
        lowest_price = float(products[0]['data-productminprice'])
    except IndexError:
        print("CENEO BLAD\n\n\n\HAAAALOOO")
        return None

    print(f"ceneo: {ceneo_name} - {lowest_price}")
    return lowest_price


if __name__ == "__main__":

    data = [
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 8GB/2666 CL16 1.20V czarna CMK8GX4M2A2666C16',
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 8GB/2666 RED CMK8GX4M1A2666C16R',
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 8GB/2400 RED CMK8GX4M1A2400C14R',
        'Pamięć RAM PATRIOT Viper Steel 2x8GB 4133MHz PVS416G413C9K',
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 8GB/3000 (1*8GB) Black CL16 CMK8GX4M1D3000C16',
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 16GB/2400 CL14-16-16-31',
        'Pamięć RAM CORSAIR DDR4 Vengeance LPX 16GB/2133(2*8GB) CMK16GX4M2A2133C13',
        'Pamięć RAM PATRIOT DDR4 Signature 8GB 2666 UDIMM (PC4-21300) PSD48G266681',
        'Intel® Core™ i7-11700K BOX (BX8070811700K)'
    ]

    for product in data:
        search_ceneo(product)
