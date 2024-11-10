import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging
from parserCard import get_html
from urllib.parse import urljoin

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("downloader.log"),
        logging.StreamHandler()
    ]
)

def download_files(html, base_url, download_folder="downloads"):
    """
    Парсит HTML-код, ищет ссылки на ТЗ и проект контракта, скачивает их, и возвращает пути к файлам.

    :param html: HTML-код страницы
    :param base_url: Базовый URL для формирования абсолютных ссылок
    :param download_folder: Папка, куда будут сохранены файлы
    :return: Кортеж (путь_к_тз, путь_к_проекту_контракта) или выбрасывает исключение
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    soup = BeautifulSoup(html, "html.parser")
    tz_link = None
    project_contract_link = None

    # Ищем ссылки внутри тегов <div role="listitem" class="item">
    for div_tag in soup.find_all("div", {"role": "listitem"}):
        a_tag = div_tag.find("a", href=True)
        if not a_tag:
            continue

        href = urljoin(base_url, a_tag["href"])  # Преобразуем относительный путь в абсолютный
        text = a_tag.get_text(strip=True).lower()

        # Логирование найденных ссылок
        logging.info(f"Найдена ссылка: {href}, текст: {text}")

        # Условие для текста ссылки на ТЗ
        if ".doc" in text or ".docx" in text:
            tz_link = href

        # Условие для текста ссылки на проект контракта
        elif ".pdf" in text:
            project_contract_link = href

    if not project_contract_link:
        raise ValueError("Ссылка на проект контракта не найдена!")

    def download_file(url, folder, predefined_name=None):
        """
        Загружает файл по URL и сохраняет в указанную папку с предопределённым именем.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Если задано предопределённое имя, используем его
            if predefined_name:
                filename = predefined_name
            else:
                # Извлекаем имя файла из заголовка Content-Disposition или URL
                filename = os.path.basename(url.split("?")[0])
                content_disposition = response.headers.get("Content-Disposition")
                if content_disposition and "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"')

            file_path = os.path.join(folder, filename)
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            logging.info(f"Файл сохранён: {file_path}")
            return file_path
        except Exception as e:
            raise ValueError(f"Не удалось скачать файл: {url}. Ошибка: {e}")

    tz_path = None
    project_contract_path = None

    # Скачиваем ТЗ с предопределённым именем
    if tz_link:
        tz_path = download_file(tz_link, download_folder, predefined_name="ТЗ.docx")

    # Скачиваем проект контракта с предопределённым именем
    project_contract_path = download_file(project_contract_link, download_folder, predefined_name="Проект-контракта.pdf")

    return tz_path, project_contract_path

if __name__ == "__main__":
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://zakupki.mos.ru/auction/9864870"
        base_url = "https://zakupki.mos.ru"  # Базовый URL
        html_code = get_html(driver=driver, url=url)
        tz_file, contract_file = download_files(html_code, base_url)
        print(f"Файл ТЗ: {tz_file}")
        print(f"Файл проекта контракта: {contract_file}")
    except ValueError as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()
