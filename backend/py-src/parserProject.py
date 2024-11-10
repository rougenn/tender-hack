import pdfplumber
import re

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text

def parse_contract_details(text):
    """
    Parses contract details and product information from the given text.
    """
    # Determine if the contract requires assurance
    contract_assurance = 1 if "обеспечение исполнения" in text.lower() else 0
    
    # Extract deadline (e.g., "в течение 10 рабочих дней")
    deadline_match = re.search(r"в течение\s+(\d+)\s+(рабочих|календарных)\s+дней", text, re.IGNORECASE)
    deadlines = f"до {deadline_match.group(1)} дней" if deadline_match else None
    
    # Extract product details
    product_pattern = re.compile(r"(\d+)\s+(Шпагат джутовый.*)", re.IGNORECASE)
    products = []
    for match in re.finditer(product_pattern, text):
        product_name = match.group(2).strip()
        product = {
            "name": product_name,
            "price": None,  # Assuming no explicit price
            "кол-во": match.group(1)
        }
        products.append(product)
    
    # Ensure products list is None if empty
    products = products if products else None
    
    # Compile the final dictionary
    return {
        "contract": contract_assurance,
        "law": "44-ФЗ",
        "deadlines": deadlines,
        "products": products
    }

def extract_contract_details_from_pdf(file_path):
    """
    Reads a PDF file and returns extracted contract details as a dictionary.
    """
    text = extract_text_from_pdf(file_path)
    return parse_contract_details(text)
