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
                
                # Sirf PDF aur Images allow ki gayi hain, baqi ignore ho jayengi
                if f_mime in ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]:
                    files_data.append({
                        "mime_type": f_mime, 
                        "data": f_bytes,
                        "filename": file.filename
                    })
                    print(f"✅ Fast File Added: {file.filename} ({f_mime})")
                else:
                    print(f"⚠️ Unsupported file ignored: {file.filename}")
    
    try:
        ai_data = extract_test_data(text, files_data)
        print("✅ AI ne final test data successfully extract kar liya hai.")
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=error_message)
    
    output_file = generate_word_file(
        academy_name, subject, class_name, test_date, time_allowed, syllabus, long_q_marks, ai_data, template_style
    )
    print("✅ MS Word final exam file tayyar ho gayi hai.")
    
    return FileResponse(
        output_file, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        filename="Generated_Test.docx"
    )