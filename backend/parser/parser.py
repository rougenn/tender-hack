from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Модифицированная функция для парсинга блоков с классом "AuctionViewSpecificationCardStyles__CardContainer-sc-1bupkfz-0"
def parse_ui_grid_objects(html):
    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    # Ищем все объекты с классом "AuctionViewSpecificationCardStyles__CardContainer-sc-1bupkfz-0"
    objects = soup.find_all("div", class_="AuctionViewSpecificationCardStyles__CardContainer-sc-1bupkfz-0")
    
    # Список для хранения характеристик каждого объекта
    all_objects_data = []
    
    for obj in objects:
        # Используем defaultdict для хранения ключ-значение пар для текущего объекта
        data_dict = defaultdict(list)
        characteristics_count = 0  # Переменная для подсчета характеристик для текущего объекта
        
        # Ищем все строки с характеристиками, пока не найдем "График поставки"
        characteristics = obj.find_all("div", class_="LabeledValue-sc-10trpha-0")
        
        for characteristic in characteristics:
            # Извлекаем текст ключа и значения
            label = characteristic.find("label").get_text(strip=True)
            value_div = characteristic.find("div")
            value_text = value_div.get_text(strip=True) if value_div else ""
            
            # Проверяем, достигли ли мы раздела "график поставки"
            if "график поставки" in label.lower():
                break  # Прекращаем сбор характеристик для текущего объекта
            
            # Убираем дублирование ключа в значении
            if value_text.startswith(label):
                value_text = value_text[len(label):].strip()
            
            # Удаляем символы \xa0
            value_text = value_text.replace('\xa0', '')
            
            # Добавляем значение в data_dict и увеличиваем счетчик характеристик
            data_dict[label].append(value_text)
            characteristics_count += 1
        
        # Сохраняем данные для текущего объекта
        all_objects_data.append({
            "characteristics": data_dict,
            "count": characteristics_count
        })

    # Печатаем количество характеристик и их значения для каждого объекта
    for i, obj_data in enumerate(all_objects_data, start=1):
        print(f"Объект {i}: Количество характеристик до 'график поставки' = {obj_data['count']}")
        print("Характеристики:", obj_data["characteristics"])
    
    return all_objects_data



# Функция для загрузки HTML-кода страницы
def get_html(driver, url):
    # Открываем страницу
    driver.get(url)
    
    # Ожидание появления первого элемента с кнопкой "Показать подробную информацию"
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//span[@id='show-more-button']"))
    )

    # Находим все кнопки "Показать подробную информацию"
    show_more_buttons = driver.find_elements(By.XPATH, "//span[@id='show-more-button']")
    
    # Нажимаем на все кнопки "Показать подробную информацию"
    for button in show_more_buttons:
        driver.execute_script("arguments[0].scrollIntoView(true);", button)  # Прокручиваем страницу к кнопке
        button.click()  # Кликаем по кнопке
        time.sleep(0.4)  # Ждем 2 секунды, чтобы страница успела обновиться после клика

    # Получаем HTML-код страницы после нажатия на все кнопки
    html = driver.page_source
    return html


def main():
    # Настройка Chrome-драйвера
    options = Options()
    options.headless = True  # если хотите запускать в фоновом режиме
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Путь к драйверу Chrome
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # URL страницы
        
        
        
        
        
        url = "https://zakupki.mos.ru/auction/9862366"
        
        # Получаем HTML-код страницы
        html_code = get_html(driver, url)
        
        # Печатаем или сохраняем HTML-код
        parsed_data = parse_ui_grid_objects(html_code)
        # print(parsed_data)
        
    finally:
        # Закрываем драйвер
        driver.quit()

if __name__ == "__main__":
    main()
