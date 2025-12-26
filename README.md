# 🩺 MediScan - Intelligent Medical Report Summarizer

MediScan is an AI-powered web application that transforms complex medical reports into clear, understandable insights. Using advanced Natural Language Processing (NLP) techniques, it extracts key information from medical documents including diagnoses, symptoms, medications, test results, and recommendations.

## ✨ Features

- **Intelligent Analysis**: Automatically extracts key medical information from reports
- **Comprehensive Summarization**: Provides executive summaries and detailed breakdowns
- **Multi-Category Extraction**: Identifies:
  - Diagnoses
  - Symptoms
  - Key Findings
  - Medications
  - Tests & Procedures
  - Recommendations
- **Confidence Scoring**: Provides analysis confidence metrics
- **Modern Web Interface**: Clean, responsive UI for easy interaction
- **RESTful API**: Backend API for integration with other systems

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
- **Flask** - Web framework
- **spaCy** - Advanced NLP library
- **NLTK** - Natural Language Toolkit
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript** - Interactivity

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- A modern web browser

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "mediscan Project"
```

### 2. Set Up Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment (recommended):

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

### 3. Set Up Frontend

The frontend is a static website. No additional setup is required. Simply open `frontend/index.html` in a web browser or serve it using a web server.

## 🎯 Usage

### Running the Backend Server

1. Navigate to the backend directory:
```bash
cd backend
```

2. Activate your virtual environment (if not already activated)

3. Run the Flask application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Accessing the Frontend

**Option 1: Direct File Access**
- Open `frontend/index.html` directly in your web browser

**Option 2: Using a Local Server (Recommended)**
- Use Python's built-in HTTP server:
```bash
cd frontend
python -m http.server 8000
```
- Then open `http://localhost:8000` in your browser

**Option 3: Using the Flask Server**
- The Flask server can also serve static files (if configured)

## 📡 API Endpoints

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Home
- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns API information and available endpoints

#### 2. Health Check
- **URL**: `/api/health`
- **Method**: `GET`
- **Description**: Returns API health status

#### 3. Summarize Report
- **URL**: `/api/summarize`
- **Method**: `POST`
- **Description**: Analyzes and summarizes a medical report
- **Request Body**:
```json
{
  "text": "Medical report text here..."
}
```
- **Response**: JSON object containing:
  - Executive summary
  - Diagnoses
  - Symptoms
  - Key findings
  - Medications
  - Tests & procedures
  - Recommendations
  - Confidence score
  - Processing time

#### 4. Demo
- **URL**: `/api/demo`
- **Method**: `GET`
- **Description**: Returns a sample analysis using a demo medical report

## 📁 Project Structure

```
mediscan Project/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration settings
│   ├── nlp_processor.py       # NLP processing logic
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Data models
│   ├── utils/                 # Utility functions
│   └── venv/                  # Virtual environment (gitignored)
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── scripts/
│   │   └── app.js             # Frontend JavaScript
│   └── styles/
│       └── style.css          # Stylesheet
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Configuration

The backend configuration can be modified in `backend/config.py`. Common settings include:
- Server port
- Debug mode
- CORS settings
- NLP model configurations

## ⚠️ Important Disclaimer

**MediScan provides AI-generated summaries for informational purposes only. This tool does not provide medical advice. Always consult with qualified healthcare professionals for medical diagnosis and treatment.**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Specify your license here]

## 👥 Authors

[Add author information here]

## 🙏 Acknowledgments

- spaCy team for the excellent NLP library
- NLTK contributors
- Flask development team

---

**Version**: 1.0.0  
**Last Updated**: 2025

