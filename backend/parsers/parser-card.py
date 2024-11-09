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
        # Пример: "31.10.2024 09:10:11"
        parsed_date = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
        return parsed_date.strftime("%d %B %Y, %H:%M:%S")  # Пример: "31 октября 2024, 09:10:11"
    except ValueError:
        # Если формат неизвестен, возвращаем оригинальную строку
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
    """
    Парсинг параметров страницы, таких как условия исполнения контракта и т.д.
    
    :param soup: Объект BeautifulSoup
    :return: Словарь с параметрами страницы
    """
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
            
            # Форматируем дату для поля "Даты проведения"
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

        # Извлекаем основные данные
        for label in [
            "Количество", "Цена за ед.", "Общая стоимость", "Код ОКПД2", 
            "Наименование ОКПД2", "Код КПГЗ", "Наименование КПГЗ",
            "Модель", "Производитель", "Даты поставки", "Адрес", "Детали поставки"
        ]:
            element = card.find("label", string=label)
            if element:
                value = element.find_next_sibling("div").get_text(strip=True)
                
                # Форматируем дату, если метка соответствует
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

def run_parser(url):
    """
    Основная функция для запуска парсера. 
    
    :param url: URL-адрес страницы
    :return: Словарь с параметрами страницы и списком продуктов
    """
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
    url = "https://zakupki.mos.ru/auction/9862366"
    parsed_data = run_parser(url)

    # Красивый вывод результатов
    print("\nПараметры страницы:")
    for key, value in parsed_data["Параметры страницы"].items():
        print(f"  {key}: {value}")

    print("\nПродукты:")
    for product in parsed_data["Продукты"]:
        print("\nПродукт:")
        for key, value in product.items():
            if key == "Характеристики":
                print(f"  {key}:")
                for char_key, char_value in value.items():
                    print(f"    {char_key}: {char_value}")
            else:
                print(f"  {key}: {value}")
    