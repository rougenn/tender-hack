import os
import json
from downloader import download_files
from parserCard import get_html, parse_page_parameters, parse_product_data, transform_data
from parserTz import parse_tz_docx
from parserProject import extract_contract_details_from_pdf
from analyze import validate_data
from bs4 import BeautifulSoup


def process_url(url):
    """
    Функция принимает URL, выполняет всю последовательность парсинга, скачивания и анализа.
    Возвращает URL и массив результатов анализа.
    """
    # Папка для сохранения файлов
    download_folder = "downloads"
    base_url = "https://zakupki.mos.ru"

    # Загрузка HTML
    html_code = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        # Настройки headless-режима
        options = Options()
        options.add_argument("--headless")  # Запуск без графического интерфейса
        options.add_argument("--no-sandbox")  # Устранение проблем с доступом
        options.add_argument("--disable-dev-shm-usage")  # Оптимизация памяти
        options.add_argument("--disable-gpu")  # Отключение GPU для стабильности
        options.add_argument("--log-level=3")  # Уменьшение уровня логов
        options.add_argument("--window-size=1920,1080")  # Установка размера окна для headless

        # Запуск драйвера
        service = Service("/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)

        html_code = get_html(driver, url)
        driver.quit()
    except Exception as e:
        return url, f"Ошибка загрузки HTML: {e}"

    # Скачивание файлов
    try:
        tz_file, project_file = download_files(html_code, base_url, download_folder=download_folder)
    except Exception as e:
        return url, f"Ошибка скачивания файлов: {e}"

    # Парсинг страницы (parserCard)
    try:
        soup = BeautifulSoup(html_code, "html.parser")
        page_parameters = parse_page_parameters(soup)
        products = parse_product_data(soup)
        parsed_data_card = {"Параметры страницы": page_parameters, "Продукты": products}
        transformed_card = transform_data(parsed_data_card)
    except Exception as e:
        return url, f"Ошибка парсинга карточки: {e}"

    # Парсинг ТЗ (parserTz)
    parsed_tz = None
    if tz_file:
        try:
            parsed_tz = parse_tz_docx(tz_file)
        except Exception as e:
            return url, f"Ошибка парсинга ТЗ: {e}"

    # Парсинг проекта (parserProject)
    parsed_project = None
    if project_file:
        try:
            parsed_project = extract_contract_details_from_pdf(project_file)
        except Exception as e:
            return url, f"Ошибка парсинга проекта контракта: {e}"

    # Если ТЗ нет, используем данные из parserProject
    if parsed_tz is None and parsed_project:
        parsed_tz = parsed_project

    # Валидация данных
    try:
        d1 = transformed_card
        d2 = parsed_project or {}
        d3 = parsed_tz or {}
        analysis_results = validate_data(d1, d2, d3)
    except Exception as e:
        return url, f"Ошибка анализа данных: {e}"

    # Вернуть результат
    return url, analysis_results
