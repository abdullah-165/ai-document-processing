import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
import re

# ✅ If Tesseract is installed, set its path here (Windows default path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ----------- 1️⃣ Extract text from an image using OCR -----------
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return clean_text(text)

# ----------- 2️⃣ Extract text from a PDF -----------
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return clean_text(text)

# ----------- 3️⃣ Extract text from a webpage -----------
def extract_text_from_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=" ")
    return clean_text(text)

# ----------- 🧹 Clean text -----------
def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces/newlines
    return text.strip()

# ----------- 🚀 TEST THE FUNCTIONS -----------
if __name__ == "__main__":
    # Example: Image OCR
    print(extract_text_from_image("test.jpeg"))

    # Example: PDF
    print(extract_text_from_pdf("testpdf.pdf"))

    # Example: Webpage
    print(extract_text_from_webpage("https://en.wikipedia.org/wiki/Lionel_Messi"))
