import csv
from docx import Document

def load_docx(doc_path):
    """
    Загрузить документ .docx.
    :param doc_path: Путь к файлу .docx.
    :return: Объект документа.
    """
    try:
        return Document(doc_path)
    except Exception as e:
        raise FileNotFoundError(f"Ошибка при загрузке документа: {e}")

def process_tables(document):
    """
    Обработать таблицы из документа и извлечь данные.
    :param document: Объект документа.
    :return: Список строк данных.
    """
    data = []
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() if cell.text.strip() else "N/A" for cell in row.cells]

            # Пропускаем строки с недостаточным количеством ячеек
            if len(cells) < 4:
                continue

            # Извлечение данных
            row_data = [
                cells[1] if len(cells) > 1 else "N/A",  # Наименование
                cells[2] if len(cells) > 2 else "N/A",  # Кол-во
                cells[3] if len(cells) > 3 else "N/A"   # Характеристика
            ]

            # Добавляем строку в данные, если она содержит полезную информацию
            if any(value != "N/A" for value in row_data):
                data.append(row_data)
    return data

def save_to_csv(data, csv_path):
    """
    Сохранить данные в файл CSV.
    :param data: Список строк данных.
    :param csv_path: Путь для сохранения CSV файла.
    """
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Данные успешно сохранены в {csv_path}")
    except Exception as e:
        raise IOError(f"Ошибка при сохранении данных в CSV: {e}")

def main(doc_path, csv_path):
    """
    Основная функция для обработки документа и сохранения данных.
    :param doc_path: Путь к входному файлу .docx.
    :param csv_path: Путь для сохранения выходного CSV.
    """
    try:
        # Загрузка документа
        document = load_docx(doc_path)

        # Обработка таблиц и извлечение данных
        data = process_tables(document)

        # Сохранение данных в CSV
        save_to_csv(data, csv_path)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример вызова
if __name__ == "__main__":
    doc_path = "path/to/your/document.docx"  # Задайте путь к вашему .docx
    csv_path = "path/to/output.csv"         # Задайте путь для сохранения CSV
    main(doc_path, csv_path)
