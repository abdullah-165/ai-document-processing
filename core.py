# core.py
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import os
from datetime import datetime

# --- Paths & folders ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
SAVE_DIR = "extracted"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- helpers ----------
def clean_and_truncate(text: str, max_words: int = 300) -> str:
    """Normalize whitespace and keep only the first `max_words` words."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    words = text.split()
    return " ".join(words[:max_words])

def save_to_file(source_type: str, text: str) -> str:
    """Save text to extracted/<type>_YYYYmmdd_HHMMSS.txt and return path."""
    filename = f"{source_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(SAVE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

# ---------- extractors ----------
def extract_text_from_image(image_path: str):
    """OCR image → clean+truncate → save → return (text, file_path)."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    text = clean_and_truncate(text)
    file_path = save_to_file("image", text) if text else None
    return text, file_path

def extract_text_from_pdf(pdf_path: str):
    """Read PDF → text → clean+truncate → save → return (text, file_path)."""
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    text = clean_and_truncate(text)
    file_path = save_to_file("pdf", text) if text else None
    return text, file_path

def extract_text_from_webpage(url: str):
    """GET HTML → strip to text → clean+truncate → save → return (text, file_path)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ")
        text = clean_and_truncate(text)
        file_path = save_to_file("web", text) if text else None
        return text, file_path
    except Exception as e:
        return f"❌ Error fetching webpage: {e}", None

# ---------- stats ----------
def analyze_word_stats(text: str):
    words = text.split()
    num_words = len(words)
    avg_word_length = np.mean([len(w) for w in words]) if words else 0.0
    return {
        "number_of_words": num_words,
        "average_word_length": round(float(avg_word_length), 2)
    }

# ---------- grammar (LanguageTool public) ----------
def check_grammar(text: str, language: str = "en-US"):
    """Returns a list of issues. No API key required (public endpoint; be gentle)."""
    url = "https://api.languagetool.org/v2/check"
    payload = {"text": text, "language": language}
    resp = requests.post(url, data=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    issues = []
    for match in data.get("matches", []):
        start = match.get("offset", 0)
        length = match.get("length", 0)
        problem = text[start:start + length]
        suggestions = [r.get("value", "") for r in match.get("replacements", [])[:3]]
        issues.append({
            "message": match.get("message", ""),
            "problem": problem,
            "suggestions": suggestions if suggestions else ["No suggestion"]
        })
    return issues
