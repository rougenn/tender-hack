from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler()
    ]
)

def format_date(date_string):
    """
    Форматирует строку с датой в приятный формат.
    
    :param date_string: Строка с датой.
    :return: Форматированная дата или оригинальная строка, если формат неизвестен.
    """
    try:
        parsed_date = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
        return parsed_date.strftime("%d %B %Y, %H:%M:%S")  # Пример: "31 октября 2024, 09:10:11"
    except ValueError:
        return date_string

def get_html(driver, url):
    logging.info(f"Открытие страницы: {url}")
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//span[@id='show-more-button']"))
    )

    show_more_buttons = driver.find_elements(By.XPATH, "//span[@id='show-more-button']")
    for button in show_more_buttons:
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        button.click()
        time.sleep(0.4)

    html = driver.page_source
    logging.info("HTML-код страницы успешно загружен.")
    return html

def parse_page_parameters(soup):
    logging.info("Парсинг параметров страницы.")
    page_parameters = {}
    parameters_labels = [
        "Условия исполнения контракта",
        "Обеспечение исполнения контракта",
        "Заказчик",
        "Заключение происходит в соответствии с законом",
        "Даты проведения"
    ]

    for label in parameters_labels:
        element = soup.find("label", string=label)
        if element:
            value = element.find_next_sibling("div").get_text(strip=True)
            if label == "Даты проведения":
                try:
                    date_range = value.split("по")
                    start_date = format_date(date_range[0].strip().replace("c", ""))
                    end_date = format_date(date_range[1].strip())
                    value = f"{start_date} — {end_date}"
                except (IndexError, ValueError):
                    pass
            page_parameters[label] = value

    logging.info(f"Параметры страницы: {page_parameters}")
    return page_parameters

def parse_product_data(soup):
    logging.info("Начало парсинга данных о продуктах.")
    product_cards = soup.find_all("div", class_="AuctionViewSpecificationCardStyles__CardContainer-sc-1bupkfz-0")

    parsed_products = []

    for card in product_cards:
        product_data = defaultdict(list)
        characteristics = {}

        # Извлекаем имя продукта
        name_element = card.find("a", class_="AuctionViewSpecificationCardStyles__CardHeader-sc-1bupkfz-1")
        if name_element:
            product_data["Имя продукта"] = name_element.get_text(strip=True)
        else:
            product_data["Имя продукта"] = "Не указано"

        # Извлекаем основные данные
        for label in [
            "Количество", "Цена за ед.", "Общая стоимость", "Код ОКПД2", 
            "Наименование ОКПД2", "Код КПГЗ", "Наименование КПГЗ",
            "Модель", "Производитель", "Даты поставки", "Адрес", "Детали поставки"
        ]:
            element = card.find("label", string=label)
            if element:
                value = element.find_next_sibling("div").get_text(strip=True)
                if label == "Даты поставки":
                    value = format_date(value)
                product_data[label] = value

        # Извлекаем характеристики
        characteristics_block = card.find(
            "div",
            class_="AuctionViewSpecificationCardStyles__BlockHeader-sc-1bupkfz-3",
            string="Характеристики",
        )
        if characteristics_block:
            higher_level_block = characteristics_block
            for _ in range(3):
                higher_level_block = higher_level_block.find_parent("div")
                if not higher_level_block:
                    break

            if higher_level_block:
                rows = higher_level_block.find_all("div", class_="row")
                for row in rows:
                    name_element = row.find("span", class_="AuctionViewSpecificationCardStyles__CharacteristicTableName-sc-1bupkfz-6")
                    value_element = row.find("span", class_="EllipsedSpan__WordBreakSpan-sc-r2mbuv-0")

                    if name_element and value_element:
                        name = name_element.get_text(strip=True)
                        value = value_element.get_text(strip=True)
                        characteristics[name] = value

        product_data["Характеристики"] = characteristics
        parsed_products.append(product_data)

    logging.info(f"Парсинг завершен. Найдено продуктов: {len(parsed_products)}")
    return parsed_products

def transform_data(parsed_data):
    """
    Преобразует данные от парсера в указанный формат.
    
    :param parsed_data: Словарь с параметрами страницы и продуктами
    :return: Преобразованный словарь
    """
    transformed = {}

    # Преобразуем параметры страницы
    page_params = parsed_data.get("Параметры страницы", {})
    transformed["contract"] = 1 if page_params.get("Обеспечение исполнения контракта", "").lower() != "не требуется" else 0
    transformed["law"] = page_params.get("Заключение происходит в соответствии с законом", "")
    
    # Определяем максимальный срок поставки (N)
    products = parsed_data.get("Продукты", [])
    max_days = 0
    for product in products:
        date_string = product.get("Даты поставки", "")
        if "до" in date_string:
            try:
                days = int(date_string.split("до")[-1].strip().split(" ")[0])
                max_days = max(max_days, days)
            except ValueError:
                pass
    transformed["deadlines"] = max_days

    # Преобразуем продукты
    transformed_products = []
    for product in products:
        transformed_product = {}

        # Добавляем имя продукта
        transformed_product["name"] = product.get("Имя продукта", "")

        # Извлекаем цену и убираем лишние символы
        price_string = product.get("Цена за ед.", "")
        price = "".join(filter(str.isdigit, price_string))
        transformed_product["price"] = price

        # Добавляем остальные характеристики
        characteristics = product.get("Характеристики", {})
        for key, value in characteristics.items():
            transformed_product[key] = value

        transformed_products.append(transformed_product)

    transformed["products"] = transformed_products

    return transformed

def run_parser(url):
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        html_code = get_html(driver, url)
        soup = BeautifulSoup(html_code, "html.parser")
        
        page_parameters = parse_page_parameters(soup)
        products = parse_product_data(soup)
        
        return {"Параметры страницы": page_parameters, "Продукты": products}
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://zakupki.mos.ru/auction/9864533"
    parsed_data = run_parser(url)

    # Преобразование данных
    transformed_data = transform_data(parsed_data)

    # Вывод преобразованных данных
    print(json.dumps(transformed_data, ensure_ascii=False, indent=2))