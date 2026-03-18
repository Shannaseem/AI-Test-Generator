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

# 🚀 NAYA PARAMETERS ADD KIYE GAYE HAIN
def extract_test_data(text, files_data=[], short_t="8", short_a="5", long_t="3", long_a="2", long_parts="no", magic_prompt=""):
    global current_key_index
    
    master_data = {
        "mcqs": [],
        "short_qs": [],
        "long_qs": []
    }
    
    parts_rule = "Divide each long question into 'Part (a)' and 'Part (b)'." if long_parts == "yes" else "Do NOT divide long questions into parts. Keep them as single full questions."
    user_magic = f"User's Special Instructions: {magic_prompt}" if magic_prompt else "No special instructions. Just make a standard high-quality exam."
    
    # 🚀 ADVANCED PROMPT ENGINEERING
    prompt_instruction = f"""
    You are an expert Educational Data Extractor AI. 
    Analyze the attached material thoroughly and generate an exam paper based on these STRICT rules:
    
    1. Short Questions: Extract exactly {short_t} short questions. 
    2. Long Questions: Extract exactly {long_t} long questions. {parts_rule}
    3. {user_magic}
    
    Return ONLY a valid JSON object with this exact structure (NO extra text, NO markdown formatting outside JSON):
    {{
        "mcqs": [
            {{"question": "...", "a": "...", "b": "...", "c": "...", "d": "...", "answer": "..."}}
        ],
        "short_qs": [
            {{"text": "..."}}
        ],
        "long_qs": [
            {{"text": "..."}}
        ]
    }}
    Note: If a long question has parts, format it cleanly like "a) [text] \\nb) [text]" inside the "text" string field.
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
                    if attempt < max_attempts - 1:
                        current_key_index = (current_key_index + 1) % len(API_KEYS)
                        configure_active_key()
                        time.sleep(2)
                    else:
                        raise Exception("RATE_LIMIT_WAIT:45")
                else:
                    return {"mcqs": [], "short_qs": [], "long_qs": []}
                    
        return {"mcqs": [], "short_qs": [], "long_qs": []}

    if text and text.strip():
        data = process_item_with_ai([prompt_instruction, f"TEXT TO ANALYZE:\n{text}"], "Text Box Content")
        master_data["mcqs"].extend(data.get("mcqs", []))
        master_data["short_qs"].extend(data.get("short_qs", []))
        master_data["long_qs"].extend(data.get("long_qs", []))
        
    if files_data:
        for idx, f in enumerate(files_data):
            file_name_label = f.get("filename", f"File {idx + 1}")
            if f["mime_type"] == "text/plain":
                file_text = f["data"].decode('utf-8')
                if len(file_text.strip()) < 5: continue
                payload = f"--- DOCUMENT TEXT ---\n{file_text}\n--- END ---"
                data = process_item_with_ai([prompt_instruction, payload], file_name_label)
            else:
                payload = {"mime_type": f["mime_type"], "data": f["data"]}
                data = process_item_with_ai([prompt_instruction, payload], file_name_label)
            
            master_data["mcqs"].extend(data.get("mcqs", []))
            master_data["short_qs"].extend(data.get("short_qs", []))
            master_data["long_qs"].extend(data.get("long_qs", []))

    return master_data