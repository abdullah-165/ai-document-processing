from fastapi import FastAPI, UploadFile, Form
from worker import process_image_task, process_pdf_task, process_web_task, process_grammar_task
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/process/image")
async def process_image(file: UploadFile):
    """Upload an image and send it to Celery worker."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = process_image_task.delay(file_path)  # send to Celery
    return {"task_id": task.id, "status": "processing"}


@app.post("/process/pdf")
async def process_pdf(file: UploadFile):
    """Upload a PDF and send it to Celery worker."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = process_pdf_task.delay(file_path)
    return {"task_id": task.id, "status": "processing"}


@app.post("/process/web")
async def process_web(url: str = Form(...)):
    """Extract text from a webpage."""
    task = process_web_task.delay(url)
    return {"task_id": task.id, "status": "processing"}


@app.post("/process/grammar")
async def process_grammar(text: str = Form(...)):
    """Check grammar of text."""
    task = process_grammar_task.delay(text)
    return {"task_id": task.id, "status": "processing"}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Get the result of a Celery task."""
    from worker import celery_app
    result = celery_app.AsyncResult(task_id)

    if result.ready():
        return {"task_id": task_id, "status": "completed", "result": result.get()}
    else:
        return {"task_id": task_id, "status": "processing"}
