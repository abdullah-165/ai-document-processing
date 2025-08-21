import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
import re
import numpy as np

# ✅ If Tesseract is installed, set its path here (Windows default path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ----------- Utility: Save Text to File -----------
def save_to_file(text, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


# ----------- 1️⃣ Extract text from an image using OCR -----------
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    text = clean_text(text)
    text = limit_words(text, 300)
    save_to_file(text, "image_output.txt")
    return text

# ----------- 2️⃣ Extract text from a PDF -----------
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    text = clean_text(text)
    text = limit_words(text, 300)
    save_to_file(text, "pdf_output.txt")
    return text

# ----------- 3️⃣ Extract text from a webpage -----------
def extract_text_from_webpage(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ")
        text = clean_text(text)
        text = limit_words(text, 300)
        save_to_file(text, "web_output.txt")
        return text
    except Exception as e:
        print(f"❌ Error fetching webpage: {e}")
        return ""


# ----------- 🧹 Clean text -----------
def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces/newlines
    return text.strip()

# ----------- 📏 Limit to 300 words -----------
def limit_words(text, max_words=300):
    words = text.split()
    return " ".join(words[:max_words])

# ----------- 📏 Word Statistics -----------
def analyze_word_stats(text):
    words = text.split()
    num_words = len(words)
    avg_word_length = np.mean([len(word) for word in words]) if words else 0

    return {
        "number_of_words": num_words,
        "average_word_length": avg_word_length
    }


# ----------- 📝 Grammar Check (Fixed) -----------
def check_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    payload = {"text": text, "language": "en-US"}
    response = requests.post(url, data=payload)
    result = response.json()

    print("\nGrammar & Spelling Issues Found:")
    for match in result.get("matches", []):
        problem = text[match['offset']:match['offset']+match['length']]
        # Extract up to 3 suggestion values (if available)
        suggestions = [r['value'] for r in match.get('replacements', [])[:3]]
        suggestions_text = ", ".join(suggestions) if suggestions else "No suggestion"

        print(f"- {match['message']}")
        print(f"  Problem: '{problem}'")
        print(f"  Suggestion: {suggestions_text}\n")

    return result


# ----------- 🚀 TEST THE FUNCTIONS -----------
if __name__ == "__main__":
    # 1️⃣ Image OCR
    print("\n===== IMAGE OCR =====")
    img_text = extract_text_from_image("test.jpeg")
    print(img_text[:300], "...\n")
    img_stats = analyze_word_stats(img_text)
    print(f"Number of Words: {img_stats['number_of_words']}")
    print(f"Average Word Length: {img_stats['average_word_length']:.2f} characters")
    check_grammar(img_text)

    # 2️⃣ PDF
    print("\n===== PDF EXTRACTION =====")
    pdf_text = extract_text_from_pdf("testpdf.pdf")
    print(pdf_text[:300], "...\n")
    pdf_stats = analyze_word_stats(pdf_text)
    print(f"Number of Words: {pdf_stats['number_of_words']}")
    print(f"Average Word Length: {pdf_stats['average_word_length']:.2f} characters")
    check_grammar(pdf_text)

    # 3️⃣ Webpage
    print("\n===== WEBPAGE EXTRACTION =====")
    web_text = extract_text_from_webpage("https://en.wikipedia.org/wiki/Lionel_Messi")
    print(web_text[:300], "...\n")
    web_stats = analyze_word_stats(web_text)
    print(f"Number of Words: {web_stats['number_of_words']}")
    print(f"Average Word Length: {web_stats['average_word_length']:.2f} characters")
    check_grammar(web_text)
