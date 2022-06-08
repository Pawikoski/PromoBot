import re


def clear_product_name(product_name: str, store_name: str, category_name: str):
    category = category_name.lower().strip()
    product = product_name.lower().strip()
    store = store_name.lower().strip()
    print(category, product, store)

    avans_delete_strings = {
        "cpus": ["procesor", ],
        "cases": ["obudowa", ],
        "gpus": ["karta graficzna", ],
        "headphones": ["słuchawki", ],
        "keyboards": ["klawiatura", ],
        "laptops": ["laptop", ],
        "monitors": ["monitor", ],
        "motherboards": ["płyta główna", ],
        "mouses": ["mysz", ],
        "psus": ["zasilacz", ],
        "ram": ["pamięć ram", ],
        "ssd": ["dysk", "ssd"],
        "smartbands": ["smartband", ],
        "smartwatches": ["smartwatch", "zegarek sportowy"],
        "sound cards": ["karta dźwiękowa", ],
        "tvs": ["telewizor", "przenośny"],
        "thermal pastes": ["pasta termoprzewodząca", ],
    }

    mediaexpert_delete_strings = {
        "cpus": ["procesor", ],
        "cases": ["obudowa", ],
        "gpus": ["karta graficzna", ],
        "hdd": ["dysk", ],
        "headphones": ["słuchawki", "nauszne", "douszne", "dokanałowe"],
        "keyboards": ["klawiatura", ],
        "laptops": ["laptop", ],
        "monitors": ["monitor", ],
        "motherboards": ["płyta główna", ],
        "mouses": ["mysz", ],
        "psus": ["zasilacz", ],
        "ram": ["pamięć ram", ],
        "ssd": ["dysk", "ssd"],
        "smartbands": ["smartband", ],
        "smartwatches": ["smartwatch", "zegarek sportowy"],
        "tvs": ["telewizor", "przenośny"],
        "thermal pastes": ["pasta termoprzewodząca", ],
    }

    morele_delete_strings = {
        "cpus": ["procesor", ", oem", ", box", ", mpk"],
        "cases": ["obudowa", ],
        "gpus": ["karta graficzna", ],
        "hdd": ["dysk", ],
        "headphones": ["słuchawki", "nauszne", "douszne", "dokanałowe"],
        "keyboards": ["klawiatura", ],
        "laptops": ["laptop", ],
        "monitors": ["monitor", ],
        "motherboards": ["płyta główna", ],
        "mouses": ["mysz", ],
        "pc fans": ["wentylator", ],
        "psus": ["zasilacz", ],
        "ram": ["pamięć ram", "pamięć"],
        "ssd": ["dysk ssd", "dysk"],
        "smartbands": ["smartband", ],
        "smartwatches": ["smartwatch", "zegarek sportowy"],
        "sound cards": ["karta dźwiękowa", "karta"],
        "tvs": ["telewizor", "przenośny"],
        "thermal pastes": ["pasta termoprzewodząca", ],
    }

    neonet_delete_strings = {
        "cpus": ["procesor", ],
        "cases": ["obudowa do komputera", "obudowa"],
        "gpus": ["karta graficzna", ],
        "keyboards": ["klawiatura", ],
        "laptops": ["laptop", ],
        "monitors": ["monitor", ],
        "mouses": ["mysz komputerowa", "mysz", "myszka"],
        "pc fans": ["wentylator komputerowy", "wentylator"],
        "psus": ["zasilacz do komputera", "zasilacz"],
        "ram": ["pamięć ram", "pamięć"],
        "smartbands": ["smartband", ],
        "smartwatches": ["smartwatch", "zegarek sportowy"],
        "tvs": ["telewizor", "przenośny"],
    }

    oleole_delete_strings = {
        "cpus": ["oem", "box", "mpk"],
    }

    sferis_delete_strings = {
        "cpus": ["procesor", ],
        "cases": ["obudowa", ],
        "gpus": ["karta graficzna", ],
        "hdd": ["hdd", ],
        "monitors": ["monitor", ],
        "motherboards": ["płyta główna", ],
        "psus": ["zasilacz", ],
        "sound cards": ["karta dźwiękowa", "karta muz.", "karta muzyczna zewn.", "karta muzyczna"],
        "ssd": ["ssd", ],
        "tvs": ["telewizor", ]
    }

    match store:
        case 'avans':
            try:
                for delete_string in avans_delete_strings[category]:
                    product = product.replace(delete_string, "")

                if category == 'tvs':
                    # matches everything up to '(1-3 digits)"'
                    re_result = re.findall(r'^(.*?)\d{1,3}\"', product)
                    if len(re_result) > 0:
                        product = re_result[0]

                return product.strip()
            except KeyError:
                return product

        case 'media expert':
            try:
                for delete_string in mediaexpert_delete_strings[category]:
                    product = product.replace(delete_string, "")
                if category == 'tvs':
                    # matches everything up to '(1-3 digits)"'
                    re_result = re.findall(r'^(.*?)\d{1,3}\"', product)
                    if len(re_result) > 0:
                        product = re_result[0]

                return product.strip()

            except KeyError:
                return product

        case "morele":
            try:
                for delete_string in morele_delete_strings[category]:
                    product = product.replace(delete_string, "")

                # Excluding store model, matches everything to '('
                re_result = re.findall(r'^(.*?)\(', product)
                if len(re_result) > 0:
                    product = re_result[0]

                return product.strip()
            except KeyError:
                return product

        case "neonet":
            try:
                for delete_string in neonet_delete_strings:
                    product = product.replace(delete_string, "")

                return product.strip()
            except KeyError:
                return product

        case 'oleole':
            try:
                for delete_string in oleole_delete_strings:
                    product = product.replace(delete_string, "")
                if category == 'cpus':
                    # Excluding store model, matches everything to '('
                    re_result = re.findall(r'^(.*?)\(', product)
                    if len(re_result) > 0:
                        product = re_result[0]

                    return product.strip()
            except KeyError:
                return product

        case 'rtv euro agd':
            try:
                for delete_string in oleole_delete_strings:
                    product = product.replace(delete_string, "")
                if category == 'cpus':
                    # Excluding store model, matches everything to '('
                    re_result = re.findall(r'^(.*?)\(', product)
                    if len(re_result) > 0:
                        product = re_result[0]

                    return product.strip()
            except KeyError:
                return product

        case 'sferis':
            try:
                for delete_string in sferis_delete_strings:
                    product = product.replace(delete_string, "")

                return product.strip()
            except KeyError:
                return product

        case 'x-kom':
            return product.strip()


