---

# 🚀 AI Test Generator PRO

An intelligent, multimodal, and fully automated exam paper creator developed by **Muhammad Shan Naseem**. This platform empowers educators, academies, and teachers to instantly generate high-quality, professional test papers in MS Word (`.docx`) format using Google's state-of-the-art **Gemini 2.5 Flash AI**.

## ✨ Premium Features

### 🧠 1. Advanced AI Extraction (Gemini 2.5 Flash)

- **Deep Content Analysis**: Intelligently scans syllabus text, book pages, and notes.
- **Smart Categorization**: Automatically extracts and categorizes content into Multiple Choice Questions (MCQs), Short Questions, and Long Questions.
- **Anti-Laziness Prompting**: Uses strict prompt engineering to force the AI to process every single uploaded file thoroughly without skipping data.

### 📂 2. Multimodal Input & Smart UI

- **Unified Smart Box**: Modern drag-and-drop zone that accepts Text, Images (PNG, JPG, WEBP), and PDFs simultaneously.
- **Live File Previews**: Instantly generates thumbnail previews for images and icon indicators for PDFs with built-in removal mechanism.
- **App-Like Experience**: 100vh locked-scroll, fully responsive interface with floating input labels, glassmorphism elements, and smooth slide-up animations.

### ⚙️ 3. Bulletproof Backend Architecture

- **Auto-Retry & Rate Limiting**: Intelligently handles API rate limits (HTTP 429). Triggers frontend countdown and dynamically retries without page reload.
- **Multi-Key Support**: Automatically rotates between multiple Gemini API keys for uninterrupted service.
- **Automated MS Word Export**: Dynamically formats AI's JSON output into beautifully structured, ready-to-print `.docx` files. Supports single-table and professional two-column formats.

---

## 🛠️ Technology Stack

### Frontend

- HTML5, CSS3 (Modern Floating Labels, CSS Grid/Flexbox)
- Vanilla JavaScript (ES6+, Async/Await, Fetch API)
- FontAwesome Icons

### Backend

- Python 3.9+
- FastAPI (High-performance API framework)
- Uvicorn (ASGI Web Server)
- Google Generative AI SDK (`google-generativeai`)
- Python-Docx (Word file manipulation)
- PyMuPDF / Pillow (Document and image handling)

---

## 🚀 Local Setup & Installation

Follow these steps to run the project locally.

### Prerequisites

- Python 3.8+ installed
- Google Gemini API Keys (Get from [Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/Shannaseem/AI-Test-Generator.git
cd AI-Test-Generator
```

### Step 2: Backend Setup

1. Navigate to the backend directory or stay in root.
2. Create virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Create `.env` file in `backend/` folder (git-ignored):

```env
GEMINI_API_KEY_1=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
```

5. Start FastAPI server:

```bash
cd backend
python -m uvicorn main:app --reload
```

_The backend runs at `http://127.0.0.1:8000`_

### Step 3: Frontend Setup

1. Open `frontend/` folder.
2. Launch `index.html` using local server (VS Code **Live Server** extension recommended).
3. Platform is ready to use!

---

## 📁 Project Structure

```
AI-Test-Generator/
│
├── backend/                    # Python FastAPI Backend
│   ├── templates/             # Custom docx templates
│   ├── main.py               # API endpoints & file handling
│   ├── ai_service.py         # Gemini AI integration & extraction
│   ├── doc_generator.py      # MS Word document formatting
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # API Keys (Git-ignored)
│
├── frontend/                  # Client-Side UI
│   ├── index.html            # Main UI Layout
│   ├── style.css             # Modern styling & animations
│   └── script.js             # API calls, Drag/Drop, Progress bar
│
├── .gitignore                # Security rules
└── README.md                 # Project Documentation
```

---
