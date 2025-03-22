from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF
import re
import pandas as pd

app = FastAPI()

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF."""
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text("text") + "\n"
    return text.strip()

def extract_invoice_fields(text):
    """Extract structured fields from invoice text using regex."""
    
    fields = {
        "Claim Amount": 0,
        "Diagnosis": "",
        "Hospital Name": "",
        "Treatment Details": ""
    }

    # Example regex patterns (modify as per invoice format)
    claim_amount_match = re.search(r"Claim Amount:\s*\$?(\d+[\.\d+]*)", text)
    diagnosis_match = re.search(r"Diagnosis:\s*(.*)", text)
    hospital_match = re.search(r"Hospital Name:\s*(.*)", text)
    treatment_match = re.search(r"Treatment Details:\s*(.*)", text)

    if claim_amount_match:
        fields["Claim Amount"] = float(claim_amount_match.group(1))
    
    if diagnosis_match:
        fields["Diagnosis"] = diagnosis_match.group(1)

    if hospital_match:
        fields["Hospital Name"] = hospital_match.group(1)

    if treatment_match:
        fields["Treatment Details"] = treatment_match.group(1)

    return fields

@app.post("/extract/")
async def extract_invoice_data(file: UploadFile = File(...)):
    try:
        # Extract text from PDF
        pdf_bytes = await file.read()
        extracted_text = extract_text_from_pdf(pdf_bytes)

        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in the PDF.")

        # Extract structured fields
        invoice_data = extract_invoice_fields(extracted_text)

        return {
            "filename": file.filename,
            "invoice_data": invoice_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
