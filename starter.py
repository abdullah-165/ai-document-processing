import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
import re
import numpy as np

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

# ----------- 📏 Word Statistics -----------
def analyze_word_stats(text):
    words = text.split()
    num_words = len(words)
    avg_word_length = np.mean([len(word) for word in words]) if words else 0

    return {
        "number_of_words": num_words,
        "average_word_length": avg_word_length
    }


def check_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    payload = {"text": text, "language": "en-US"}
    
    try:
        response = requests.post(url, data=payload, timeout=10)  # 10 sec timeout
        response.raise_for_status()
        result = response.json()

        print("\nGrammar & Spelling Issues Found:")
        for match in result["matches"]:
            print(f"- {match['message']}")
            print(f"  Problem: '{text[match['offset']:match['offset']+match['length']]}'")
            print(f"  Suggestion: {', '.join(match['replacements'][:3])}\n")
        return result
    
    except requests.exceptions.Timeout:
        print("❌ Error: Connection to LanguageTool timed out. Please check your internet or try again later.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")




# ----------- 🚀 TEST THE FUNCTIONS -----------
if __name__ == "__main__":
    # 1️⃣ Image OCR
    print("\n===== IMAGE OCR =====")
    img_text = extract_text_from_image("test.jpeg")
    print(img_text[:300], "...\n")
    img_stats = analyze_word_stats(img_text)
    print(f"Number of Words: {img_stats['number_of_words']}")
    print(f"Average Word Length: {img_stats['average_word_length']:.2f} characters")
    check_grammar(img_text)  # ✅ Grammar check for image text

    # 2️⃣ PDF
    print("\n===== PDF EXTRACTION =====")
    pdf_text = extract_text_from_pdf("testpdf.pdf")
    print(pdf_text[:300], "...\n")
    pdf_stats = analyze_word_stats(pdf_text)
    print(f"Number of Words: {pdf_stats['number_of_words']}")
    print(f"Average Word Length: {pdf_stats['average_word_length']:.2f} characters")
    check_grammar(pdf_text)  # ✅ Grammar check for PDF text

    # 3️⃣ Webpage
    print("\n===== WEBPAGE EXTRACTION =====")
    web_text = extract_text_from_webpage("https://en.wikipedia.org/wiki/Lionel_Messi")
    print(web_text[:300], "...\n")
    web_stats = analyze_word_stats(web_text)
    print(f"Number of Words: {web_stats['number_of_words']}")
    print(f"Average Word Length: {web_stats['average_word_length']:.2f} characters")
    check_grammar(web_text)  # ✅ Grammar check for webpage text

