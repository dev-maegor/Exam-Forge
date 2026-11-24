# <span style="color:#397d78">ExamForge</span>

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

## 🌐 Live Prototype

**[Open ExamForge · Streamlit](https://examforge.streamlit.app/)**

No local setup is required to try the deployed prototype.
Please wait for the app to rebuild if it has gone in sleep mode.
It might take a minute or two.

---

## 🎓 AI-powered examination question generation

**ExamForge** helps faculty members and teaching assistants turn study documents into structured assessment questions.

Upload a PDF or TXT file, choose the question formats and difficulty, and generate a polished question set with answers and explanations.

## ❓ What the Project Does

ExamForge converts uploaded educational material into an editable question set for faculty and teaching assistants.

It extracts readable text from PDF or TXT documents, sends the study material to the Gemini API, and generates:

- Multiple Choice Questions
- True/False Questions
- Short Answer Questions

Generated questions include answer choices where applicable, correct answers, explanations, difficulty information and per-question quality scores.

Faculty can copy the complete question set or download it as a TXT file for use in an examination paper.

---

## ✨ Features

- 📄 PDF and TXT document extraction
- 🧠 Gemini-powered question generation
- 🎯 Easy, Medium and Hard difficulty levels
- ✅ Multiple Choice Questions
- 🔤 True/False Questions
- ✍️ Short Answer Questions
- 🔢 Individual counts for every question type
- 📊 Per-question quality scoring
- 📋 Copy and download generated questions
- 🌙 Light and dark themes
- 🔁 Automatic bounded API retry handling

---

## 🖥️ Application Pages

| Page | Purpose |
|---|---|
| **Generate** | Upload study material and configure the question set |
| **Generated Questions** | Review, copy or download generated questions |
| **About** | Learn about ExamForge and its workflow |

---

## 🔧 Technology

- **Python**
- **Streamlit**
- **Google Gemini API**
- **PyMuPDF**
- **python-dotenv**
- **Pandas**

---

## 🚀 Getting Started

### Open the deployed prototype

Visit **[https://examforge.streamlit.app/](https://examforge.streamlit.app/)**.

### Run locally

### 1. Clone the repository

```bash
git clone https://github.com/dev-maegor/Exam-Forge.git
cd Exam-Forge
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

For Streamlit Community Cloud, add the key under:

**Settings → Secrets**

```toml
GEMINI_API_KEY = "your_api_key_here"
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🔐 Security

Never commit your API key.

The repository ignores `.env`, `.venv`, Streamlit secrets and local test scripts.

---

## 🗂️ Project Structure

```text
ExamForge/
├── app.py
├── config.py
├── requirements.txt
├── modules/
│   ├── document_processor.py
│   └── question_generator.py
├── prompts/
│   ├── generation_v1.py
│   ├── generation_v2.py
│   └── generation_v3.py
└── README.md
```

---

## 👩‍🏫 Intended Users

- Faculty members
- Teaching assistants
- Educators
- Academic content creators

---

## 👥 Team Members

| Name | Student ID |
|---|---|
| Dishubh Singh | S24CSEU0808 |
| Gadde Tanishq | S24CSEU0793 |

## 📝 License

This project is intended for educational use.

