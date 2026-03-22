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

def extract_test_data(text, files_data=[], short_t="8", short_a="5", long_t="3", long_a="2", exam_pattern="chapter", short_groups="1", magic_prompt="", bilingual="no"):
    global current_key_index

    master_data = {"mcqs": [], "short_qs": [], "long_qs": []}

    # SMART EXAM PATTERN LOGIC
    if exam_pattern == "board":
        try:
            short_groups_int = int(short_groups)
        except:
            short_groups_int = 2
        parts_rule = "Divide each long question into 'Part (a)' and 'Part (b)'."
    else:
        short_groups_int = 1
        parts_rule = "Do NOT divide long questions into parts. Keep them as single full questions."

    total_short_needed = int(short_t) * short_groups_int
    
    # MAGIC BOX OVERRIDE
    user_magic = f"CRITICAL USER INSTRUCTION: {magic_prompt}" if magic_prompt else "Standard comprehensive extraction."

    if bilingual == "yes":
        language_rule = "BILINGUAL MODE IS ON: Generate BOTH English and Urdu (Nastaleeq script). Use separate fields for English (e.g., q_en) and Urdu (e.g., q_ur)."
        json_schema = '{"mcqs": [{"q_en": "...", "q_ur": "...", "a_en": "...", "a_ur": "...", "b_en": "...", "b_ur": "...", "c_en": "...", "c_ur": "...", "d_en": "...", "d_ur": "...", "answer": "a"}], "short_qs": [{"text_en": "...", "text_ur": "..."}], "long_qs": [{"text_en": "...", "text_ur": "..."}]}'
    else:
        language_rule = "Generate all questions in English only. Do NOT include any '_ur' fields."
        json_schema = '{"mcqs": [{"q_en": "...", "a_en": "...", "b_en": "...", "c_en": "...", "d_en": "...", "answer": "a"}], "short_qs": [{"text_en": "..."}], "long_qs": [{"text_en": "..."}]}'

    # SUPER STRICT PROMPT
    prompt_instruction = f"""
You are a highly advanced Educational Test Creator AI. 
Your task is to analyze ALL provided content (Text, PDF text, and Images) deeply and comprehensively.
DO NOT skip any concepts.

REQUIREMENTS:
1. Extract or generate highly relevant MCQs from the material. Do not miss important details.
2. Generate exactly {total_short_needed} Short Questions.
3. Generate exactly {long_t} Long Questions. {parts_rule}
4. {language_rule}
5. {user_magic}

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this schema exactly. NO markdown, NO explanations, ONLY JSON:
{json_schema}
Note: For long questions with parts, use "a) text\\nb) text".
"""

    model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={"max_output_tokens": 8192, "temperature": 0.4})

    def process_item_with_ai(content_list):
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

    # COMBINING ALL DATA INTO A SINGLE CALL FOR BETTER AI UNDERSTANDING
    ai_payload = [prompt_instruction]
    
    if text and text.strip():
        ai_payload.append(f"--- USER TEXT EXCERPT ---\n{text}\n--- END TEXT ---")
        
    if files_data:
        for f in files_data:
            if f["mime_type"] == "text/plain":
                file_text = f["data"].decode('utf-8')
                ai_payload.append(f"--- ATTACHED DOCUMENT ---\n{file_text}\n--- END DOCUMENT ---")
            else:
                ai_payload.append({"mime_type": f["mime_type"], "data": f["data"]})

    master_data = process_item_with_ai(ai_payload)

    if not master_data.get("mcqs") and not master_data.get("short_qs") and not master_data.get("long_qs"):
        raise Exception("AI could not extract valid data. Please ensure the uploaded images/documents contain readable syllabus text.")

    return master_data


# ==========================================
# NEW: LIVE AI EDITOR FUNCTION
# ==========================================
def refine_test_data(current_json_str, refine_prompt):
    global current_key_index
    model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={"max_output_tokens": 8192, "temperature": 0.5})
    
    instruction = f"""
    You are an AI Test Editor. Here is the current test paper in JSON format:
    {current_json_str}

    The teacher wants to modify this paper. Here is their explicit command:
    "{refine_prompt}"

    Apply the requested changes to the JSON structure. 
    - Keep the exact same JSON keys (`mcqs`, `short_qs`, `long_qs`).
    - If they asked to add questions, add them. If they asked to replace, replace them.
    - DO NOT change the structure. DO NOT add markdown text outside the JSON.
    - Return ONLY the updated valid JSON.
    """
    
    max_attempts = len(API_KEYS)
    for attempt in range(max_attempts):
        try:
            response = model.generate_content([instruction])
            raw_text = response.text.strip()
            
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
            if json_match: raw_text = json_match.group(1)
            else:
                start = raw_text.find('{')
                end = raw_text.rfind('}')
                if start != -1 and end != -1: raw_text = raw_text[start:end+1]
            return json.loads(raw_text)
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                if attempt < max_attempts - 1:
                    current_key_index = (current_key_index + 1) % len(API_KEYS)
                    configure_active_key()
                    time.sleep(2)
                else: raise Exception("RATE_LIMIT_WAIT:45")
    raise Exception("Failed to refine test due to AI limits.")