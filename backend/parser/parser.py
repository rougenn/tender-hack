from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

# Функция для парсинга блоков с классом "ui grid"
def parse_ui_grid_blocks(html):
    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    # Ищем все блоки с классом "ui grid"
    grid_blocks = soup.find_all("div", class_="ui grid")
    
    # Используем defaultdict для хранения ключ-значение пар с несколькими значениями
    data_dict = defaultdict(list)
    
    for block in grid_blocks:
        # Находим все элементы с текстом внутри блока
        labels = block.find_all("label")
        values = block.find_all("div", class_="LabeledValue-sc-10trpha-0")
        
        # Для каждого label находим соответствующее значение
        for label, value in zip(labels, values):
            key = label.get_text(strip=True)
            value_text = value.get_text(strip=True)
            data_dict[key].append(value_text)  # Добавляем значение в список для данного ключа

    return data_dict

# Функция для загрузки HTML-кода страницы
def get_html(driver, url):
    # Открываем страницу
    driver.get(url)
    
    # Ожидание появления элемента с текстом "Количество" внутри нужного блока
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='LabeledValue-sc-10trpha-0 eDzBib']/label[text()='Количество']"))
    )
    
    # Ожидание изменения структуры страницы
    html = driver.page_source
    while True:
        time.sleep(1)
        new_html = driver.page_source
        if new_html != html:  # Страница изменилась
            html = new_html
        else:
            break  # Страница больше не меняется, можно продолжать
    return html

def main():
    # Настройка Firefox-драйвера
    options = Options()
    options.headless = True  # Запуск в фоновом режиме, если нужно

    driver = webdriver.Firefox(options=options)

    try:
        # URL страницы
        url = "https://zakupki.mos.ru/auction/9864533"
        
        # Получаем HTML-код страницы
        html_code = get_html(driver, url)
        
        # Печатаем или сохраняем HTML-код
        # print(html_code)
        parsed_data = parse_ui_grid_blocks(html_code)
        print(parsed_data)
        
    finally:
        # Закрываем драйвер
        driver.quit()

if __name__ == "__main__":
    main()
