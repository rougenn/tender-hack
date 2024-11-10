from typing import List, Dict, Union

def equal(str1: str, str2: str) -> bool:
    """
    Проверяет равенство двух строк.
    """
    return str1 == str2

def validate_data(d1: Dict, d2: Dict, d3: Dict) -> List[int]:
    """
    Проверяет данные d1, d2, d3 по 6 критериям.

    :param d1: Данные из parser-card.
    :param d2: Данные из parser-project.
    :param d3: Данные из parser-tz.
    :return: Список из 6 элементов (0 или 1), где 1 - критерий пройден, 0 - не пройден.
    """
    results = [1] * 6  # Изначально все критерии считаются выполненными

    # Преобразуем данные для удобства
    def extract_products(data: Dict) -> Dict[str, Dict]:
        """
        Извлекает продукты из данных.
        """
        if data.get("products") is None:
            return None
        return {product["name"]: product for product in data["products"]}

    products_d1 = extract_products(d1)
    products_d2 = extract_products(d2)
    products_d3 = extract_products(d3)

    # 1. Названия продуктов совпадают
    if products_d1 is not None:
        if products_d2 is not None:
            for name in products_d2:
                if name not in products_d1:
                    results[0] = 0
                    break
        if products_d3 is not None:
            for name in products_d3:
                if name not in products_d1:
                    results[0] = 0
                    break
    elif products_d2 is not None or products_d3 is not None:
        results[0] = 0

    # 2. Поле "контракт" совпадает
    contract_d2 = d2.get("contract")
    contract_d3 = d3.get("contract")
    if not (contract_d2 is None or equal(d1["contract"], contract_d2)) and \
       not (contract_d3 is None or equal(d1["contract"], contract_d3)):
        results[1] = 0

    # 3. Поле "law" совпадает
    law_d2 = d2.get("law")
    law_d3 = d3.get("law")
    if not (law_d2 is None or equal(d1["law"], law_d2)) and \
       not (law_d3 is None or equal(d1["law"], law_d3)):
        results[2] = 0

    # 4. Поле "дедлайн" совпадает
    deadlines_d2 = d2.get("deadlines")
    deadlines_d3 = d3.get("deadlines")
    if not (deadlines_d2 is None or equal(d1["deadlines"], deadlines_d2)) and \
       not (deadlines_d3 is None or equal(d1["deadlines"], deadlines_d3)):
        results[3] = 0

    # 5. Цены продуктов совпадают
    if products_d1 is not None:
        if products_d2 is not None:
            for name, product in products_d2.items():
                if name not in products_d1 or not equal(products_d1[name]["price"], product["price"]):
                    results[4] = 0
                    break
        if products_d3 is not None:
            for name, product in products_d3.items():
                if name not in products_d1 or not equal(products_d1[name]["price"], product["price"]):
                    results[4] = 0
                    break

    # 6. Ключи и значения продуктов совпадают
    if products_d2 is not None:
        for name, product in products_d2.items():
            if name in products_d1:
                for key, value in product.items():
                    if key != "price" and not equal(products_d1[name].get(key, None), value):
                        results[5] = 0
                        break
    if products_d3 is not None:
        for name, product in products_d3.items():
            if name in products_d1:
                for key, value in product.items():
                    if key != "price" and not equal(products_d1[name].get(key, None), value):
                        results[5] = 0
                        break

    return results
