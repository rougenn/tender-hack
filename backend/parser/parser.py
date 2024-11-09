from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Функция для парсинга блоков с классом "ui grid"
def parse_ui_grid_blocks(html):
    print(html)
    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    # Ищем все блоки с классом "ui grid"
    grid_blocks = soup.find_all("div", class_="ui grid")
    
    # Используем defaultdict для хранения ключ-значение пар
    data_dict = defaultdict(list)
    
    for block in grid_blocks:
        labels = block.find_all("label")
        values = block.find_all("div", class_="LabeledValue-sc-10trpha-0")
        
        for label, value in zip(labels, values):
            key = label.get_text(strip=True)
            value_text = value.get_text(strip=True)
            
            # Убираем дублирование ключа в значении
            if value_text.startswith(key):
                value_text = value_text[len(key):].strip()
            
            # Удаляем символы \xa0
            value_text = value_text.replace('\xa0', '')
            
            # Добавляем значение в data_dict
            data_dict[key].append(value_text)

    # Создаем новый словарь, содержащий только каждый второй элемент для каждого ключа
    filtered_data_dict = {key: values[::2] for key, values in data_dict.items()}

    return filtered_data_dict


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
        url = "https://zakupki.mos.ru/auction/9864533"
        
        # Получаем HTML-код страницы
        html_code = get_html(driver, url)
        
        # Печатаем или сохраняем HTML-код
        parsed_data = parse_ui_grid_blocks(html_code)
        print(parsed_data)
        
    finally:
        # Закрываем драйвер
        driver.quit()

if __name__ == "__main__":
    main()
