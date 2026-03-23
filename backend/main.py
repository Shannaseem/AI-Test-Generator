from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from ai_service import extract_test_data
from doc_generator import generate_word_file
import os
import subprocess
import traceback
import json
import datetime
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False, allow_methods=["*"],
    allow_headers=["*"], expose_headers=["Content-Disposition"]
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("\n=== ❌ CRITICAL BACKEND ERROR ❌ ===")
    traceback.print_exc()
    print("====================================\n")
    return JSONResponse(status_code=500, content={"detail": f"Server crashed: {str(exc)}"}, headers={"Access-Control-Allow-Origin": "*"} )

# Unified Test Builder Function (Single Source of Formatting)
async def build_test_process(
    academy_name, subject, class_name, test_date, time_allowed, syllabus,
    long_q_marks, template_style, short_total, short_attempt, exam_pattern,
    short_groups, long_total, long_attempt, bilingual, magic_prompt,
    generate_answer_key, text, files
):
    print(f"\n--- Processing Test: {academy_name} ---")

    files_data = []
    if files:
        for file in files:
            if file.filename:
                f_bytes = await file.read()
                f_mime = file.content_type
                if f_mime in ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]:
                    files_data.append({"mime_type": f_mime, "data": f_bytes, "filename": file.filename})

    try:
        # Step 1: Run AI
        ai_data = extract_test_data(
            text=text, files_data=files_data, short_t=short_total, short_a=short_attempt,
            long_t=long_total, long_a=long_attempt, exam_pattern=exam_pattern, short_groups=short_groups,
            magic_prompt=magic_prompt, bilingual=bilingual
        )
        print("✅ Step 1: AI JSON extracted.")

        # Step 2: Generate Word File (.docx) instantly for formatting truth
        docx_path = generate_word_file(
            academy_name=academy_name, subject=subject, class_name=class_name, test_date=test_date,
            time_allowed=time_allowed, syllabus=syllabus, long_q_marks=long_q_marks, ai_data=ai_data,
            template_style=template_style, short_total=short_total, short_attempt=short_attempt,
            exam_pattern=exam_pattern, short_groups=short_groups, long_total=long_total, long_attempt=long_attempt,
            bilingual=bilingual, generate_answer_key=generate_answer_key
        )
        print(f"✅ Step 2: DOCX generated at {docx_path}.")

        # Step 3: Server-side PDF Conversion (Requires LibreOffice on Render)
        pdf_path = docx_path.replace(".docx", ".pdf")
        pdf_status = "ok"
        try:
            # Command to check if libreoffice is available
            check_libre = shutil.which("libreoffice")
            if check_libre:
                print("Step 3a: LibreOffice found. Converting DOCX to PDF...")
                result = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(os.path.abspath(docx_path)), os.path.abspath(docx_path)],
                    capture_output=True, text=True, timeout=90
                )
                if result.returncode != 0: raise Exception(f"LibreOffice error: {result.stderr}")
                print(f"✅ Step 3b: Server-side PDF created at {pdf_path}.")
            else:
                print("Step 3a: ⚠️ LibreOffice not found on server. Cannot generate PDF server-side.")
                pdf_path = None
                pdf_status = "missing_libreoffice"
        except Exception as e_pdf:
            print(f"Step 3c: ❌ Server-side PDF conversion failed: {str(e_pdf)}")
            pdf_path = None
            pdf_status = str(e_pdf)

        return docx_path, pdf_path, pdf_status, ai_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-test")
async def process_test_endpoint(
    academy_name: str = Form(...), subject: str = Form(...), class_name: str = Form(...),
    test_date: str = Form(...), time_allowed: str = Form(...), syllabus: str = Form(...),
    long_q_marks: str = Form(...), template_style: str = Form("table"), short_total: str = Form("8"),
    short_attempt: str = Form("5"), exam_pattern: str = Form("chapter"), short_groups: str = Form("1"),
    long_total: str = Form("3"), long_attempt: str = Form("2"), bilingual: str = Form("no"),
    magic_prompt: Optional[str] = Form(""), generate_answer_key: str = Form("no"),
    text: Optional[str] = Form(""), files: List[UploadFile] = File([]),
):
    docx_path, pdf_path, pdf_status, ai_data = await build_test_process(
        academy_name, subject, class_name, test_date, time_allowed, syllabus, long_q_marks,
        template_style, short_total, short_attempt, exam_pattern, short_groups,
        long_total, long_attempt, bilingual, magic_prompt, generate_answer_key, text, files
    )
    
    # We return URLs so frontend can display/download them
    return JSONResponse(content={
        "docx_filename": os.path.basename(docx_path),
        "pdf_filename": os.path.basename(pdf_path) if pdf_path else None,
        "pdf_status": pdf_status,
        "ai_data": ai_data
    })

# Simple endpoints to download the files
@app.get("/get-file/{filename}")
async def get_file(filename: str):
    file_path = filename # assume it's in the same dir for simplicity
    if os.path.exists(file_path):
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if filename.endswith(".docx") else "application/pdf"
        return FileResponse(file_path, media_type=mime, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")