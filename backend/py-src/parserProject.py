import pdfplumber
import re

def extract_text_from_pdf(file_path):
    """
    Извлекает полный текст из PDF.
    """
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text

def parse_table(rows):
    """
    Обрабатывает таблицу и возвращает список товаров.
    """
    if not rows or len(rows) < 2:  # Проверяем, что таблица имеет хотя бы заголовок и одну строку данных
        return None

    headers = [header.lower().strip() for header in rows[0]]  # Приводим заголовки к нижнему регистру
    products = []

    for row in rows[1:]:
        if not any(cell.strip() for cell in row):  # Пропускаем пустые строки
            continue
        product = {}
        for i, cell in enumerate(row):
            value = cell.strip()
            if i < len(headers):
                key = headers[i]
                if "наименование" in key or "товар" in key:
                    product["name"] = value
                elif "количество" in key or "кол-во" in key:
                    product["quantity"] = value
                elif "№" in key:
                    product["№№ п/п"] = value
                elif "ед.изм" in key:
                    product["ед.изм."] = value
                elif "цена" in key:
                    product["цена за ед., руб."] = value
                elif "сумма" in key:
                    product["сумма, руб."] = value
        if product:  # Добавляем продукт, только если он не пустой
            products.append(product)

    return products if products else None

def parse_contract_details(text):
    """
    Парсит данные контракта и продукты из текста.
    """
    # Определяем, требуется ли обеспечение контракта
    contract_assurance = 1 if "обеспечение исполнения" in text.lower() else 0
    
    # Извлечение срока поставки
    deadline_match = re.search(r"в течение\s+(\d+)\s+(рабочих|календарных)\s+дней", text, re.IGNORECASE)
    deadlines = f"до {deadline_match.group(1)} дней" if deadline_match else None
    
    # Парсим таблицу товаров
    products = None
    table_pattern = re.compile(r"(?:№.*?\n.*?Наименование.*?)\n(.*)", re.IGNORECASE | re.DOTALL)
    table_match = table_pattern.search(text)
    if table_match:
        table_text = table_match.group(1)
        rows = [row.split("\t") for row in table_text.split("\n") if row.strip()]
        products = parse_table(rows)

    return {
        "contract": contract_assurance,
        "law": "44-ФЗ",
        "deadlines": deadlines,
        "products": products
    }

def extract_contract_details_from_pdf(file_path):
    """
    Извлекает данные контракта из PDF и возвращает их в виде словаря.
    """
    text = extract_text_from_pdf(file_path)
    return parse_contract_details(text)

