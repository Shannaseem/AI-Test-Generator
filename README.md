````markdown
# 🚀 AI Test Generator PRO

An intelligent, multimodal, and fully automated exam paper creator developed by **Muhammad Shan Naseem**. This platform empowers educators, academies, and teachers to instantly generate high-quality, professional test papers in MS Word (`.docx`) format using Google's state-of-the-art **Gemini 2.5 Flash AI**.

---

## ✨ Premium Features

### 🧠 1. Advanced AI Extraction (Gemini 2.5 Flash)

- **Deep Content Analysis**: Intelligently scans syllabus text, book pages, and notes.
- **Smart Categorization**: Automatically extracts and categorizes content into Multiple Choice Questions (MCQs), Short Questions, and Long Questions.
- **Anti-Laziness Prompting**: Uses strict prompt engineering to force the AI to process every single uploaded file thoroughly without skipping data or hallucinating new questions when strictly extracting.

### 🌍 2. Perfect Bilingual Formatting (Invisible Grid)

- **Side-by-Side Excellence**: Seamlessly supports English and Urdu (Nastaleeq script) in the same document.
- **Invisible Grid System**: Uses an advanced zero-border table mechanism to ensure English stays strictly on the left margin and Urdu stays strictly on the right, matching official Board paper standards perfectly.

### ✍️ 3. Interactive AI Editor (Magic Command Center)

- **Live Document Refinement**: Don't like a specific question? Open the preview, type a command like _"Change MCQ #3 to a harder concept"_ or _"Make Long Q1 a numerical problem"_.
- **Instant Updates**: The AI processes your command, regenerates the specific parts, and instantly refreshes the MS Word document on the exact same screen!

### 📄 4. True MS Word Preview

- **No Fake HTML**: Integrates Microsoft Office Online Viewer to show you the exact page-by-page A4 document before downloading.
- **Smart Cache-Buster**: Automatically appends dynamic timestamps to files, ensuring the preview viewer always displays your newest, freshest edits without getting stuck on old caches.

### 📂 5. Multimodal Input & Smart UI

- **Unified Smart Box**: Modern drag-and-drop zone that accepts Text, Images (PNG, JPG, WEBP), and PDFs simultaneously.
- **Clipboard Support**: Simply press `Ctrl+V` to paste images directly into the tool.
- **Smooth UX**: 100vh locked-scroll, fully responsive interface with floating input labels, glassmorphism elements, and an animated, real-time percentage progress bar.

### ⚙️ 6. Bulletproof Backend Architecture

- **Dynamic Exam Patterns**: Switch between "Chapter / Weekly Test" (Standard) or "Full Term / Board Pattern" (automatically splits long questions into parts a & b, and groups short questions).
- **Auto-Retry & Rate Limiting**: Intelligently handles API rate limits (HTTP 429). Triggers frontend countdowns and dynamically retries without page reloads.
- **Multi-Key Support**: Automatically rotates between multiple Gemini API keys for uninterrupted service.
- **Instant `.docx` Export**: Fast, reliable, and perfectly formatted export to Microsoft Word format with zero layout breakage.

---

## 🛠️ Technology Stack

### Frontend

- HTML5, CSS3 (Modern Floating Labels, CSS Grid/Flexbox, No heavy external frameworks)
- Vanilla JavaScript (ES6+, Async/Await, Fetch API, DOM Manipulation)
- FontAwesome Icons

### Backend

- Python 3.9+
- FastAPI (High-performance API framework)
- Uvicorn (ASGI Web Server)
- Google Generative AI SDK (`google-generativeai`)
- Python-Docx (Complex Word file and table manipulation)
- PyMuPDF / Pillow (Document and image handling)

---

## 🚀 Local Setup & Installation

Follow these steps to run the project locally.

### Prerequisites

- Python 3.8+ installed
- Google Gemini API Keys (Get from [Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone the Repository

```bash
git clone [https://github.com/Shannaseem/AI-Test-Generator.git](https://github.com/Shannaseem/AI-Test-Generator.git)
cd AI-Test-Generator
```
````

### Step 2: Backend Setup

1. Navigate to the project directory and create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Create a `.env` file in the `backend/` folder (git-ignored):

```env
GEMINI_API_KEY_1=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
```

4. Start the FastAPI server:

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 10000
```

_The backend runs at `http://localhost:10000`_

### Step 3: Frontend Setup

1. Open the `frontend/` folder.
2. Launch `index.html` using a local server (VS Code **Live Server** extension is highly recommended).
3. The platform is ready to use!

---

## 💡 How to Use

1. **Configure Paper:** Fill in the Academy Name, Subject, Class, Date, and select your Document Style and Language.
2. **Set Logic:** Choose between "Chapter Test" or "Board Pattern". Define exactly how many MCQs, Short, and Long questions you need.
3. **Upload Source:** Paste your syllabus text or drag & drop PDFs/Images into the Source Material box.
4. **Generate:** Click **"Build Interactive Test Paper"**.
5. **Review & Refine:** A full-screen MS Word preview will open. Use the AI Command Box at the bottom to make live edits if needed.
6. **Download:** Click **"Download Exact Word File"** and print your perfect exam!

---

## 📁 Project Structure

```text
AI-Test-Generator/
│
├── backend/                    # Python FastAPI Backend
│   ├── main.py               # API endpoints & file handling
│   ├── ai_service.py         # Gemini AI integration, extraction & refinement
│   ├── doc_generator.py      # MS Word document formatting (Invisible Grid logic)
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # API Keys (Git-ignored)
│
├── frontend/                   # Client-Side UI
│   ├── index.html            # Main UI Layout & Modal Viewer
│   ├── style.css             # Modern styling & animations
│   └── script.js             # API calls, Drag/Drop, Progress bar, Cache Busting
│
├── .gitignore                # Security rules
└── README.md                 # Project Documentation
```

---

## 👨‍💻 Developer

Designed and Developed with ❤️ by **Muhammad Shan Naseem**.  
**Date Completed:** March 2026  
**Version:** 2.0.0 (Pro Edition)

```

```
