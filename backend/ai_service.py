import os
import json
import time
import re
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

def extract_test_data(text, files_data=[], short_t="8", short_a="5", long_t="3", long_a="2", exam_pattern="chapter", magic_prompt="", bilingual="no"):
    global current_key_index

    master_data = {"mcqs": [], "short_qs": [], "long_qs": []}

    # SMART EXAM PATTERN LOGIC
    if exam_pattern == "board":
        short_groups_int = 2
        parts_rule = "Divide each long question into 'Part (a)' and 'Part (b)'."
    else:
        short_groups_int = 1
        parts_rule = "Do NOT divide long questions into parts. Keep them as single full questions."

    total_short_needed = int(short_t) * short_groups_int
    user_magic = f"User's Special Instructions: {magic_prompt}" if magic_prompt else "No special instructions."

    if bilingual == "yes":
        language_rule = "BILINGUAL MODE IS ON: Generate BOTH English and Urdu (Nastaleeq script). Use separate fields for English (e.g., q_en) and Urdu (e.g., q_ur)."
        json_schema = '{"mcqs": [{"q_en": "...", "q_ur": "...", "a_en": "...", "a_ur": "...", "b_en": "...", "b_ur": "...", "c_en": "...", "c_ur": "...", "d_en": "...", "d_ur": "...", "answer": "a"}], "short_qs": [{"text_en": "...", "text_ur": "..."}], "long_qs": [{"text_en": "...", "text_ur": "..."}]}'
    else:
        language_rule = "Generate all questions in English only. Do NOT include any '_ur' fields."
        json_schema = '{"mcqs": [{"q_en": "...", "a_en": "...", "b_en": "...", "c_en": "...", "d_en": "...", "answer": "a"}], "short_qs": [{"text_en": "..."}], "long_qs": [{"text_en": "..."}]}'

    prompt_instruction = f"""
You are an expert Educational Data Extractor AI.
Generate an exam paper based on these STRICT rules:
1. Short Questions: Extract exactly {total_short_needed} short questions.
2. Long Questions: Extract exactly {long_t} long questions. {parts_rule}
3. {language_rule}
4. {user_magic}

Return ONLY a valid JSON object with this exact structure (NO extra text):
{json_schema}
Note: If a long question has parts, format it like "a) [text]\\nb) [text]" inside the respective text field.
"""

    model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={"max_output_tokens": 8192})

    def process_item_with_ai(content_list, item_name):
        global current_key_index
        max_attempts = len(API_KEYS)

        for attempt in range(max_attempts):
            try:
                response = model.generate_content(content_list)
                raw_text = response.text.strip()
                json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
                if json_match: raw_text = json_match.group(1)
                else:
                    markdown_match = re.search(r'```\s*(.*?)\s*```', raw_text, re.DOTALL)
                    if markdown_match: raw_text = markdown_match.group(1)
                    else:
                        start = raw_text.find('{')
                        end = raw_text.rfind('}')
                        if start != -1 and end != -1: raw_text = raw_text[start:end+1]
                return json.loads(raw_text)
            except Exception as e:
                if "429" in str(e) or "Quota" in str(e) or "ResourceExhausted" in str(e):
                    if attempt < max_attempts - 1:
                        current_key_index = (current_key_index + 1) % len(API_KEYS)
                        configure_active_key()
                        time.sleep(2)
                    else: raise Exception("RATE_LIMIT_WAIT:45")
                else: return {"mcqs": [], "short_qs": [], "long_qs": []}

        return {"mcqs": [], "short_qs": [], "long_qs": []}

    if text and text.strip():
        data = process_item_with_ai([prompt_instruction, f"TEXT TO ANALYZE:\n{text}"], "Text Box")
        master_data["mcqs"].extend(data.get("mcqs", []))
        master_data["short_qs"].extend(data.get("short_qs", []))
        master_data["long_qs"].extend(data.get("long_qs", []))

    if files_data:
        for idx, f in enumerate(files_data):
            label = f.get("filename", f"File {idx + 1}")
            if f["mime_type"] == "text/plain":
                file_text = f["data"].decode('utf-8')
                if len(file_text.strip()) > 5:
                    data = process_item_with_ai([prompt_instruction, f"--- DOCUMENT ---\n{file_text}\n--- END ---"], label)
            else:
                data = process_item_with_ai([prompt_instruction, {"mime_type": f["mime_type"], "data": f["data"]}], label)
            
            master_data["mcqs"].extend(data.get("mcqs", []))
            master_data["short_qs"].extend(data.get("short_qs", []))
            master_data["long_qs"].extend(data.get("long_qs", []))

    if not master_data["mcqs"] and not master_data["short_qs"] and not master_data["long_qs"]:
        raise Exception("AI could not extract any questions. Please provide clearer text or images.")

    return master_data