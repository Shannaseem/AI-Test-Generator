from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from ai_service import extract_test_data
from doc_generator import generate_word_file
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

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
    
    # 🚀 NAYE FIELDS
    short_total: str = Form("8"),
    short_attempt: str = Form("5"),
    long_total: str = Form("3"),
    long_attempt: str = Form("2"),
    long_parts: str = Form("no"),
    magic_prompt: Optional[str] = Form(""),
    
    text: Optional[str] = Form(""),
    files: List[UploadFile] = File([]) 
):
    print(f"\n--- Nayi Request Aayi Hai: {academy_name} - {syllabus} ---")
    
    files_data = []
    
    if files:
        for file in files:
            if file.filename:
                f_bytes = await file.read()
                f_mime = file.content_type
                if f_mime in ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]:
                    files_data.append({"mime_type": f_mime, "data": f_bytes, "filename": file.filename})
    
    try:
        # AI Service ko naya data pass kiya ja raha hai
        ai_data = extract_test_data(
            text, files_data, 
            short_total, short_attempt, long_total, long_attempt, long_parts, magic_prompt
        )
        print("✅ AI ne final test data successfully extract kar liya hai.")
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=error_message)
    
    output_file = generate_word_file(
        academy_name, subject, class_name, test_date, time_allowed, syllabus, 
        long_q_marks, ai_data, template_style,
        # Yeh naya data Word Generator ko bhi bhej rahe hain
        short_total, short_attempt, long_total, long_attempt
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