from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from ai_service import extract_test_data
from doc_generator import generate_word_file
import os
import traceback
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False, allow_methods=["*"],
    allow_headers=["*"], expose_headers=["Content-Disposition"]
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running perfectly!"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("\n=== ❌ CRITICAL BACKEND ERROR ❌ ===")
    traceback.print_exc()
    print("====================================\n")
    return JSONResponse(status_code=500, content={"detail": f"Server crashed: {str(exc)}"}, headers={"Access-Control-Allow-Origin": "*"} )

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
        ai_data = extract_test_data(
            text=text, files_data=files_data, short_t=short_total, short_a=short_attempt,
            long_t=long_total, long_a=long_attempt, exam_pattern=exam_pattern, short_groups=short_groups,
            magic_prompt=magic_prompt, bilingual=bilingual
        )
        print("✅ Step 1: AI JSON extracted.")

        docx_path = generate_word_file(
            academy_name=academy_name, subject=subject, class_name=class_name, test_date=test_date,
            time_allowed=time_allowed, syllabus=syllabus, long_q_marks=long_q_marks, ai_data=ai_data,
            template_style=template_style, short_total=short_total, short_attempt=short_attempt,
            exam_pattern=exam_pattern, short_groups=short_groups, long_total=long_total, long_attempt=long_attempt,
            bilingual=bilingual, generate_answer_key=generate_answer_key
        )
        print(f"✅ Step 2: DOCX generated.")

        return docx_path, ai_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-test")
async def process_test_endpoint(
    academy_name: str = Form(...), subject: str = Form(...), class_name: str = Form(...),
    test_date: str = Form(...), time_allowed: str = Form(...), syllabus: str = Form(...),
    long_q_marks: str = Form(...), template_style: str = Form("table"), short_total: str = Form(...),
    short_attempt: str = Form(...), exam_pattern: str = Form("chapter"), short_groups: str = Form("1"),
    long_total: str = Form(...), long_attempt: str = Form(...), bilingual: str = Form("no"),
    magic_prompt: Optional[str] = Form(""), generate_answer_key: str = Form("no"),
    text: Optional[str] = Form(""), files: List[UploadFile] = File([]),
):
    docx_path, ai_data = await build_test_process(
        academy_name, subject, class_name, test_date, time_allowed, syllabus, long_q_marks,
        template_style, short_total, short_attempt, exam_pattern, short_groups,
        long_total, long_attempt, bilingual, magic_prompt, generate_answer_key, text, files
    )
    
    # 🔥 CACHE BUSTER: Unique filename every time so Preview NEVER shows old file
    clean = lambda s: s.replace(" ", "_").replace("/", "_").replace("\\", "_")
    timestamp = int(time.time())
    unique_name = f"{clean(class_name)}_{clean(subject)}_{timestamp}.docx"
    
    new_path = os.path.join(os.path.dirname(os.path.abspath(docx_path)), unique_name)
    os.rename(docx_path, new_path)

    return JSONResponse(content={
        "docx_filename": unique_name,
        "ai_data": ai_data
    })

@app.get("/get-file/{filename}")
async def get_file(filename: str):
    file_path = filename 
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")