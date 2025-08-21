# worker.py
from celery import Celery
from core import (
    extract_text_from_image,
    extract_text_from_pdf,
    extract_text_from_web,
    grammar_check,
)

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",   # Redis as broker
    backend="redis://localhost:6379/0"   # Redis as result backend
)

# Tasks wrapping your core functions

@celery_app.task
def process_image_task(file_path: str):
    """Process image and extract text (OCR)."""
    return extract_text_from_image(file_path)


@celery_app.task
def process_pdf_task(file_path: str):
    """Process PDF and extract text."""
    return extract_text_from_pdf(file_path)


@celery_app.task
def process_web_task(url: str):
    """Process webpage and extract text."""
    return extract_text_from_web(url)


@celery_app.task
def process_grammar_task(text: str):
    """Check grammar of given text."""
    return grammar_check(text)
