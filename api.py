"""
api.py
Exposes the OCR pipeline as an HTTP endpoint so other modules (frontend,
carbon calculation, etc.) can call it over the network instead of needing
to import your Python code directly.

Run with:
    uvicorn api:app --reload --port 8001

Then POST a bill image to http://localhost:8001/process-bill
"""

import os
import shutil
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from main import process_bill

app = FastAPI(title="EcoTrack AI - OCR & Bill Processing")

# Allow the frontend (different port) to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "module": "ocr-bill-processing"}


@app.post("/process-bill")
async def process_bill_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = process_bill(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {e}")
    finally:
        os.remove(tmp_path)

    return result
