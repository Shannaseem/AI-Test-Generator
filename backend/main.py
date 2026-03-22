from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from ai_service import extract_test_data, refine_test_data
from doc_generator import generate_word_file
import traceback
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("\n=== ❌ CRITICAL BACKEND ERROR ❌ ===")
    traceback.print_exc()
    print("====================================\n")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server crashed: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"} 
    )

# ==========================================
# STEP 1: PREVIEW ENDPOINT (Runs AI Extraction)
# ==========================================
@app.post("/generate-preview")
async def generate_preview_endpoint(
    short_total: str = Form("8"),
    short_attempt: str = Form("5"),
    exam_pattern: str = Form("chapter"),
    short_groups: str = Form("1"),
    long_total: str = Form("3"),
    long_attempt: str = Form("2"),
    bilingual: str = Form("no"),
    magic_prompt: Optional[str] = Form(""),
    text: Optional[str] = Form(""),
    files: List[UploadFile] = File([]),
):
    print(f"\n--- AI PREVIEW REQUEST | Pattern: {exam_pattern} ---")
    
    files_data = []
    if files:
        for file in files:
            if file.filename:
                f_bytes = await file.read()
                f_mime = file.content_type
                if f_mime in ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]:
                    files_data.append({
                        "mime_type": f_mime, "data": f_bytes, "filename": file.filename
                    })
    try:
        ai_data = extract_test_data(
            text=text, files_data=files_data, short_t=short_total, short_a=short_attempt,
            long_t=long_total, long_a=long_attempt, exam_pattern=exam_pattern, short_groups=short_groups,
            magic_prompt=magic_prompt, bilingual=bilingual
        )
        print("✅ AI JSON successfully extracted for Preview.")
        return JSONResponse(content=ai_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# STEP 1.5: REFINE PREVIEW ENDPOINT (AI Editor)
# ==========================================
@app.post("/refine-preview")
async def refine_preview_endpoint(
    ai_data_json: str = Form(...),
    refine_prompt: str = Form(...)
):
    print(f"\n--- AI REFINE REQUEST | Prompt: {refine_prompt} ---")
    try:
        updated_data = refine_test_data(ai_data_json, refine_prompt)
        print("✅ Preview Refined Successfully.")
        return JSONResponse(content=updated_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# STEP 2: DOWNLOAD ENDPOINT (Instant Word)
# ==========================================
@app.post("/generate-word")
async def generate_word_endpoint(
    academy_name: str = Form(...), subject: str = Form(...), class_name: str = Form(...),
    test_date: str = Form(...), time_allowed: str = Form(...), syllabus: str = Form(...),
    long_q_marks: str = Form(...), template_style: str = Form("table"), short_total: str = Form("8"),
    short_attempt: str = Form("5"), exam_pattern: str = Form("chapter"), short_groups: str = Form("1"),
    long_total: str = Form("3"), long_attempt: str = Form("2"), bilingual: str = Form("no"),
    generate_answer_key: str = Form("no"), ai_data_json: str = Form(...)
):
    print(f"\n--- INSTANT DOCX REQUEST: {academy_name} ---")
    ai_data = json.loads(ai_data_json)

    output_file = generate_word_file(
        academy_name=academy_name, subject=subject, class_name=class_name,
        test_date=test_date, time_allowed=time_allowed, syllabus=syllabus,
        long_q_marks=long_q_marks, ai_data=ai_data, template_style=template_style,
        short_total=short_total, short_attempt=short_attempt, exam_pattern=exam_pattern, short_groups=short_groups,
        long_total=long_total, long_attempt=long_attempt, bilingual=bilingual,
        generate_answer_key=generate_answer_key
    )
    
    clean = lambda s: s.replace(" ", "_").replace("/", "_").replace("\\", "_")
    dynamic_name = f"{clean(class_name)}_{clean(subject)}_{clean(syllabus)}.docx"

    return FileResponse(
        output_file, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dynamic_name
    )