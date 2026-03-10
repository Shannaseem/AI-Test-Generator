import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

API_KEYS = [key for key in API_KEYS if key and key.strip()]

if not API_KEYS:
    raise ValueError("❌ Koi API Key nahi mili! Please apni .env file check karein.")

current_key_index = 0

def configure_active_key():
    global current_key_index
    genai.configure(api_key=API_KEYS[current_key_index])
    print(f"🔄 Switched to API Key {current_key_index + 1}")

configure_active_key()

def extract_test_data(text, files_data=[]):
    global current_key_index
    
    master_data = {
        "mcqs": [],
        "short_qs": [],
        "long_qs": []
    }
    
    # AI ke liye strict instruction
    prompt_instruction = """
    You are an expert Educational Data Extractor AI. 
    Analyze the attached material thoroughly and extract EVERY SINGLE QUESTION you can find.
    If the text contains MCQs, extract them. If it contains short or long questions, extract them.
    
    Return ONLY a valid JSON object with this exact structure (NO extra markdown or text outside JSON):
    {
        "mcqs": [
            {"question": "...", "a": "...", "b": "...", "c": "...", "d": "...", "answer": "..."}
        ],
        "short_qs": [
            {"text": "..."}
        ],
        "long_qs": [
            {"text": "..."}
        ]
    }
    """
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"max_output_tokens": 8192}
    )
    
    def process_item_with_ai(content_list, item_name):
        global current_key_index
        max_attempts = len(API_KEYS)
        
        for attempt in range(max_attempts):
            try:
                print(f"⚡ Processing AI for [{item_name}] with Key {current_key_index + 1}...")
                response = model.generate_content(content_list)
                
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "").strip()
                    
                return json.loads(raw_text)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
                    print(f"⚠️ Key {current_key_index + 1} Limit Full during {item_name}!")
                    if attempt < max_attempts - 1:
                        current_key_index = (current_key_index + 1) % len(API_KEYS)
                        configure_active_key()
                        time.sleep(2)
                    else:
                        raise Exception("RATE_LIMIT_WAIT:45")
                else:
                    print(f"⚠️ JSON Parse Error on {item_name}: {error_msg}. Skipping this file to save the rest.")
                    return {"mcqs": [], "short_qs": [], "long_qs": []}
                    
        return {"mcqs": [], "short_qs": [], "long_qs": []}

    # 1. Pehle Text Box ka Data process karein
    if text and text.strip():
        data = process_item_with_ai([prompt_instruction, f"TEXT TO ANALYZE:\n{text}"], "Text Box Content")
        master_data["mcqs"].extend(data.get("mcqs", []))
        master_data["short_qs"].extend(data.get("short_qs", []))
        master_data["long_qs"].extend(data.get("long_qs", []))
        
    # 2. Phir Har File ko Alag se Process karein
    if files_data:
        for idx, f in enumerate(files_data):
            file_name_label = f.get("filename", f"File {idx + 1}")
            
            # 🚀 MASTER FIX FOR WORD FILE: Text ko proper wrapper ke andar bhej rahe hain
            if f["mime_type"] == "text/plain":
                file_text = f["data"].decode('utf-8')
                
                if len(file_text.strip()) < 5:
                    print(f"⚠️ Skipped AI call for {file_name_label} because text was empty.")
                    continue
                    
                payload = f"--- START OF DOCUMENT TEXT ({file_name_label}) ---\n{file_text}\n--- END OF DOCUMENT TEXT ---\n\nTASK: Please extract all MCQs, short questions, and long questions from the text above."
                data = process_item_with_ai([prompt_instruction, payload], file_name_label)
            
            # Agar PDF ya Image hai
            else:
                payload = {"mime_type": f["mime_type"], "data": f["data"]}
                data = process_item_with_ai([prompt_instruction, payload], file_name_label)
            
            # Extracted data ko master list mein jor do
            master_data["mcqs"].extend(data.get("mcqs", []))
            master_data["short_qs"].extend(data.get("short_qs", []))
            master_data["long_qs"].extend(data.get("long_qs", []))

    print(f"🎯 FINAL OUTPUT READY: {len(master_data['mcqs'])} MCQs, {len(master_data['short_qs'])} Shorts, {len(master_data['long_qs'])} Longs.")
    return master_data