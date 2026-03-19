from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from ai_service import extract_test_data
from doc_generator import generate_word_file
import os
import subprocess
import traceback # Added to track exact errors

app = FastAPI()

# --- BULLETPROOF CORS FIX ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains
    allow_credentials=False, # Set to False so "*" works perfectly
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# --- GLOBAL ERROR CATCHER ---
# This stops FastAPI from dropping CORS headers when a 500 error happens
# --- GLOBAL ERROR CATCHER ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("\n=== ❌ CRITICAL BACKEND ERROR ❌ ===")
    traceback.print_exc()  # This prints the exact crash to Render logs
    print("====================================\n")
    
    # Manually injecting CORS headers into the error response so the frontend can see it
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server crashed: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"} 
    )

# ==========================================
# HELPER: Word file generate karna
# ==========================================
async def build_test(
    academy_name, subject, class_name, test_date, time_allowed,
    syllabus, long_q_marks, template_style,
    short_total, short_attempt, short_groups,
    long_total, long_attempt, long_parts,
    bilingual, magic_prompt,
    generate_answer_key, add_watermark,
    text, files, logo
):
    print(f"\n--- Nayi Request: {academy_name} | {syllabus} ---")
    print(f"    Bilingual: {bilingual} | Groups: {short_groups} | Answer Key: {generate_answer_key} | Watermark: {add_watermark}")

    # Source files process karo
    files_data = []
    if files:
        for file in files:
            if file.filename:
                f_bytes = await file.read()
                f_mime = file.content_type
                if f_mime in ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]:
                    files_data.append({
                        "mime_type": f_mime,
                        "data": f_bytes,
                        "filename": file.filename
                    })

    # Logo process karo
    logo_bytes = None
    logo_mime = None
    if logo and logo.filename:
        logo_bytes = await logo.read()
        logo_mime = logo.content_type
        print(f"    Logo received: {logo.filename} ({logo_mime})")

    # AI se data extract karo
    try:
        ai_data = extract_test_data(
            text=text,
            files_data=files_data,
            short_t=short_total,
            short_a=short_attempt,
            long_t=long_total,
            long_a=long_attempt,
            long_parts=long_parts,
            magic_prompt=magic_prompt,
            bilingual=bilingual,
            short_groups=short_groups
        )
        print("✅ AI data successfully extract ho gaya.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Word file generate karo
    output_file = generate_word_file(
        academy_name=academy_name,
        subject=subject,
        class_name=class_name,
        test_date=test_date,
        time_allowed=time_allowed,
        syllabus=syllabus,
        long_q_marks=long_q_marks,
        ai_data=ai_data,
        template_style=template_style,
        short_total=short_total,
        short_attempt=short_attempt,
        short_groups=short_groups,
        long_total=long_total,
        long_attempt=long_attempt,
        bilingual=bilingual,
        generate_answer_key=generate_answer_key,
        add_watermark_flag=add_watermark,
        logo_bytes=logo_bytes,
        logo_mime=logo_mime
    )

    return output_file


# ==========================================
# ENDPOINT 1: Word (.docx) Download
# ==========================================
@app.post("/generate-test")
async def generate_test_endpoint(
    academy_name: str = Form(...),
    subject: str = Form(...),
    class_name: str = Form(...),
    test_date: str = Form(...),
    time_allowed: str = Form(...),
    syllabus: str = Form(...),
    long_q_marks: str = Form(...),
    template_style: str = Form("table"),
    short_total: str = Form("8"),
    short_attempt: str = Form("5"),
    short_groups: str = Form("1"),
    long_total: str = Form("3"),
    long_attempt: str = Form("2"),
    long_parts: str = Form("no"),
    bilingual: str = Form("no"),
    magic_prompt: Optional[str] = Form(""),
    generate_answer_key: str = Form("no"),
    add_watermark: str = Form("no"),
    text: Optional[str] = Form(""),
    files: List[UploadFile] = File([]),
    logo: Optional[UploadFile] = File(None),
):
    output_file = await build_test(
        academy_name, subject, class_name, test_date, time_allowed,
        syllabus, long_q_marks, template_style,
        short_total, short_attempt, short_groups,
        long_total, long_attempt, long_parts,
        bilingual, magic_prompt,
        generate_answer_key, add_watermark,
        text, files, logo
    )

    safe_class = class_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_subject = subject.replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_syllabus = syllabus.replace(" ", "_").replace("/", "_").replace("\\", "_")
    dynamic_name = f"{safe_class}_{safe_subject}_{safe_syllabus}.docx"

    return FileResponse(
        output_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dynamic_name
    )


# ==========================================
# ENDPOINT 2: PDF Export
# ==========================================
@app.post("/generate-pdf")
async def generate_pdf_endpoint(
    academy_name: str = Form(...),
    subject: str = Form(...),
    class_name: str = Form(...),
    test_date: str = Form(...),
    time_allowed: str = Form(...),
    syllabus: str = Form(...),
    long_q_marks: str = Form(...),
    template_style: str = Form("table"),
    short_total: str = Form("8"),
    short_attempt: str = Form("5"),
    short_groups: str = Form("1"),
    long_total: str = Form("3"),
    long_attempt: str = Form("2"),
    long_parts: str = Form("no"),
    bilingual: str = Form("no"),
    magic_prompt: Optional[str] = Form(""),
    generate_answer_key: str = Form("no"),
    add_watermark: str = Form("no"),
    text: Optional[str] = Form(""),
    files: List[UploadFile] = File([]),
    logo: Optional[UploadFile] = File(None),
):
    output_file = await build_test(
        academy_name, subject, class_name, test_date, time_allowed,
        syllabus, long_q_marks, template_style,
        short_total, short_attempt, short_groups,
        long_total, long_attempt, long_parts,
        bilingual, magic_prompt,
        generate_answer_key, add_watermark,
        text, files, logo
    )

    # Word ko PDF mein convert karo
    pdf_output = output_file.replace(".docx", ".pdf")

    try:
        result = subprocess.run(
            [
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", os.path.dirname(os.path.abspath(output_file)),
                os.path.abspath(output_file)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise Exception(f"LibreOffice error: {result.stderr}")

    except FileNotFoundError:
        try:
            # --- PDF FALLBACK FIX APPLIED HERE ---
            from docx2pdf import convert
            abs_output = os.path.abspath(output_file)
            abs_pdf = os.path.abspath(pdf_output)
            convert(abs_output, abs_pdf)
        except Exception as e2:
            raise HTTPException(
                status_code=500,
                detail=f"PDF conversion failed. (Note: Microsoft Word must be installed for local PDF export). Error: {str(e2)}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(pdf_output):
        raise HTTPException(status_code=500, detail="PDF file generate nahi hui.")

    safe_class = class_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_subject = subject.replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_syllabus = syllabus.replace(" ", "_").replace("/", "_").replace("\\", "_")
    dynamic_name = f"{safe_class}_{safe_subject}_{safe_syllabus}.pdf"

    return FileResponse(
        pdf_output,
        media_type="application/pdf",
        filename=dynamic_name
    )