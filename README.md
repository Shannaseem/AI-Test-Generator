# 🚀 AI Test Generator PRO

An intelligent, multimodal, and fully automated exam paper creator developed by **Muhammad Shan Naseem**. This platform empowers educators, academies, and teachers to instantly generate high-quality, professional test papers in MS Word (`.docx`) format using Google's state-of-the-art Gemini 2.5 Flash AI.

## ✨ Premium Features

### 🧠 1. Advanced AI Extraction (Gemini 2.5 Flash)

- **Deep Content Analysis:** Intelligently scans syllabus text, book pages, and notes.
- **Smart Categorization:** Automatically extracts and categorizes content into Multiple Choice Questions (MCQs), Short Questions, and Long Questions.
- **Anti-Laziness Prompting:** Uses strict prompt engineering to force the AI to process every single uploaded file thoroughly without skipping data.

### 📂 2. Multimodal Input & Smart UI

- **Unified Smart Box:** A modern drag-and-drop zone that accepts Text, Images (PNG, JPG, WEBP), and PDFs simultaneously.
- **Live File Previews:** Instantly generates thumbnail previews for images and icon indicators for PDFs with a built-in removal mechanism.
- **App-Like Experience:** A 100vh locked-scroll, fully responsive interface with floating input labels, glassmorphism elements, and smooth slide-up animations.

### ⚙️ 3. Bulletproof Backend Architecture

- **Auto-Retry & Rate Limiting:** Intelligently handles API rate limits (HTTP 429). If limits are hit, it triggers a frontend countdown and dynamically retries without page reload.
- **Multi-Key Support:** Automatically rotates between multiple Gemini API keys to ensure uninterrupted service.
- **Automated MS Word Export:** Dynamically formats the AI's JSON output into a beautifully structured, ready-to-print Microsoft Word (`.docx`) file. Supports both single-table and professional two-column formats.

---

## 🛠️ Technology Stack

**Frontend:**

- HTML5, CSS3 (Modern Floating Labels, CSS Grid/Flexbox)
- Vanilla JavaScript (ES6+, Async/Await, Fetch API)
- FontAwesome Icons

**Backend:**

- Python 3.9+
- FastAPI (High-performance API framework)
- Uvicorn (ASGI Web Server)
- Google Generative AI SDK (`google-generativeai`)
- Python-Docx (Word file manipulation)
- PyMuPDF / Pillow (For document and image handling)

---

## 🚀 Local Setup & Installation

Follow these steps to run the project locally on your machine.

### Prerequisites

- Python 3.8+ installed.
- Google Gemini API Keys (Get them from Google AI Studio).

### Step 1: Clone the Repository

```bash
git clone [https://github.com/Shannaseem/AI-Test-Generator.git](https://github.com/Shannaseem/AI-Test-Generator.git)
cd AI-Test-Generator
```

````

### Step 2: Backend Setup

1. Navigate to the backend directory (if applicable) or stay in the root folder.
2. Create a virtual environment (Recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

3. Install the required dependencies:

```bash
pip install -r backend/requirements.txt

```

4. Create a `.env` file in the `backend` folder and add your API keys (This file is git-ignored for security):

```env
GEMINI_API_KEY_1=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here

```

5. Start the FastAPI server:

```bash
cd backend
python -m uvicorn main:app --reload

```

_The backend will run at `http://127.0.0.1:8000_`

### Step 3: Frontend Setup

1. Open the `frontend` folder.
2. Launch `index.html` using a local server (like VS Code's **Live Server** extension).
3. The platform is now ready to use!

---

## 📁 Project Structure

```text
AI-Test-Generator/
│
├── backend/                  # Python FastAPI Backend
│   ├── templates/            # Custom docx templates
│   ├── main.py               # API endpoints & file handling
│   ├── ai_service.py         # Gemini AI integration & extraction logic
│   ├── doc_generator.py      # MS Word document formatting
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # API Keys (Ignored in Git)
│
├── frontend/                 # Client-Side UI
│   ├── index.html            # Main UI Layout
│   ├── style.css             # Modern styling & animations
│   └── script.js             # API calls, Drag/Drop logic, Progress bar
│
├── .gitignore                # Security rules
└── README.md                 # Project Documentation


````
