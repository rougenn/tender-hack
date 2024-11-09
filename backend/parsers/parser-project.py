import pdfplumber
import re

def extract_text(pdf_path):
    """
    Extracts text from a PDF.
    """
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def find_section_by_regex(text, patterns):
    """
    Finds text of a section based on regex patterns.
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            end = start + 2000  # Limit output to 2000 characters
            return text[start:end].strip()
    return None

def parse_specification(text):
    """
    Extracts the entire specification text based on a keyword search.
    """
    spec_pattern = r"(Спецификация.*?)(Приложение|Конец|$)"
    match = re.search(spec_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Спецификация не найдена"

def parse_pdf_criteria(pdf_path):
    """
    Parses the PDF and returns extracted data by criteria.
    """
    # Extract text from PDF
    text = extract_text(pdf_path)
    if not text:
        print(f"Unable to extract text from file: {pdf_path}")
        return {}

    # Define patterns for section search
    section_patterns = {
        "Статья 1": [r"Статья 1[:\.\s]", r"1\.\s"],
        "Статья 2": [r"Статья 2[:\.\s]", r"2\.\s"],
        "Статья 3": [r"Статья 3[:\.\s]", r"3\.\s"],
        "Статья 4": [r"Статья 4[:\.\s]", r"4\.\s"],
        "Статья 6": [r"Статья 6[:\.\s]", r"6\.\s"],
        "Статья 7": [r"Статья 7[:\.\s]", r"7\.\s"],
    }

    # Collect results for each criterion
    results = {
        "1": text.split("\n")[0].strip() if text else "Не найдено",  # Document title
        "2": "Не требуется",  # Criterion 2 is fixed
        "3": {
            "Статья 4": find_section_by_regex(text, section_patterns["Статья 4"]),
            "Статья 6": find_section_by_regex(text, section_patterns["Статья 6"]),
        },
        "4": {
            "Статья 3": find_section_by_regex(text, section_patterns["Статья 3"]),
            "Статья 4": find_section_by_regex(text, section_patterns["Статья 4"]),
        },
        "5": {
            "Статья 2": find_section_by_regex(text, section_patterns["Статья 2"]),
            "Статья 7": find_section_by_regex(text, section_patterns["Статья 7"]),
        },
        "6": {
            "Статья 1": find_section_by_regex(text, section_patterns["Статья 1"]),
            "Статья 4": find_section_by_regex(text, section_patterns["Статья 4"]),
            "Статья 6": find_section_by_regex(text, section_patterns["Статья 6"]),
            "Спецификация": parse_specification(text),
        }
    }

    # Remove duplicate sections
    for criterion, sections in results.items():
        if isinstance(sections, dict):
            unique_sections = {}
            seen_texts = set()
            for section, content in sections.items():
                if content and content not in seen_texts:
                    unique_sections[section] = content
                    seen_texts.add(content)
            results[criterion] = unique_sections

    return results

def print_results(results):
    """
    Prints the parsed results, avoiding repeating the same content.
    """
    seen_texts = set()
    for criterion, data in results.items():
        print(f"Критерий {criterion}:")
        if isinstance(data, dict):
            for section, content in data.items():
                if content and content not in seen_texts:
                    print(f"  {section}:\n{content}\n")
                    seen_texts.add(content)
        else:
            if data not in seen_texts:
                print(f"  {data}")
                seen_texts.add(data)
        print("-" * 80)

def main():
    """
    Main function.
    """
    pdf_path = input("Введите путь к PDF-файлу: ").strip()
    results = parse_pdf_criteria(pdf_path)
    print_results(results)

if __name__ == "__main__":
    main()