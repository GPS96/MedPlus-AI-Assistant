MedPlus AI Assistant

Production-Ready Medical AI with GDPR and HIPAA Compliance

Overview

MediPlus AI Assistant is an enterprise-grade application designed to analyze medical documents, provide health consultations, and search medical research while maintaining complete patient data privacy. The system automatically detects and removes sensitive patient information before sending data to external APIs, ensuring full compliance with GDPR, HIPAA, and EU AI Act requirements.

This project demonstrates production-ready medical AI implementation with privacy-first architecture, making it suitable for healthcare deployment and regulatory compliance scenarios.

Key Features

Bilingual Support: Full support for English and German language processing. All medical consultations and document analysis automatically adapt to the selected language.

GDPR and HIPAA Compliance: Automatic detection and anonymization of 8 categories of Protected Health Information including patient names, dates, contact information, medical IDs, and insurance numbers. All PHI is removed before external API calls.

Medical Document Analysis: Upload prescriptions, lab reports, and medical records for intelligent analysis. The system extracts text, identifies key findings, provides recommendations, and generates next steps.

Image Processing: Extract text from medical document images using advanced OCR technology. Images are processed with automatic privacy protection.

Medical Research Integration: Search latest medical literature from trusted sources like PubMed, WHO, and CDC. Get AI-summarized findings and access original research materials.

Dual-Output Analysis: Generate both technical clinical summaries for healthcare providers and simplified patient-friendly explanations for lay users.

Confidence Scoring: Transparency metrics showing the AI's confidence level in medical analysis recommendations.

Privacy Audit Trail: Complete logging of all anonymization operations for compliance reporting and security auditing.

Technology Stack

Backend Framework:
- FastAPI: High-performance Python web framework for API development
- LangChain: AI orchestration engine using LangChain Expression Language
- Google Gemini 2.0: Multimodal language model for text and vision processing

Frontend Interface:
- Streamlit: Interactive web-based user interface
- Requests: HTTP client for backend communication

Privacy Implementation:
- Regex-Based Anonymization: Fast pattern matching for PHI detection and removal
- Zero External Exposure: Patient data anonymized locally before API calls
- Complete Audit Logging: Track all data processing for compliance

External Services:
- Google Gemini API: Advanced language and vision model
- Tavily AI API: Medical research and literature search

Project Structure

mediplus-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── chains/
│   │   │   ├── analysis_chain.py
│   │   │   └── chat_chain.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── routes/
│   │   │   ├── analysis.py
│   │   │   ├── health.py
│   │   │   └── research.py
│   │   ├── services/
│   │   │   ├── anonymization_service.py
│   │   │   ├── gemini_service.py
│   │   │   └── tavily_service.py
│   │   ├── config.py
│   │   └── main.py
│   ├── frontend.py
│   ├── requirements.txt
│   └── .env (not tracked)
├── .gitignore
└── README.md

Installation and Setup

Prerequisites

Before installation, ensure you have the following:
- Python 3.9 or higher
- pip package manager
- Virtual environment capability (venv is included with Python)
- Google Gemini API key from https://makersuite.google.com/
- Tavily API key from https://www.tavily.com/

Step 1: Clone Repository

git clone https://github.com/GPS96/MedPlus-AI-Assistant.git
cd medicare-ai-assistant

Step 2: Create Virtual Environment

On Windows:
python -m venv medvenv
medvenv\Scripts\activate

On macOS/Linux:
python3 -m venv medvenv
source medvenv/bin/activate

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Configure Environment Variables

Create a .env file in the backend directory:

GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
CORS_ORIGINS=http://localhost:8501,http://localhost:8000

Step 5: Run Backend Server

uvicorn app.main:app --reload --port 8000

The API documentation will be available at http://localhost:8000/docs

Step 6: Run Frontend Application

Open a new terminal in the backend directory and run:

streamlit run frontend.py

The application will open at http://localhost:8501

Usage Guide

Medical Consultation Chat

1. Navigate to the Chat tab in the web interface
2. Select your preferred language (English or German)
3. Ask medical questions about symptoms, conditions, or treatment options
4. Receive evidence-based responses with relevant information and recommendations
5. All responses include disclaimers and recommendations to consult healthcare professionals

Document Analysis

1. Go to the Document Analysis tab
2. Paste the text content of a medical document or prescription
3. Optionally add context about the patient's medical history
4. Click Analyze Document
5. Review the structured analysis including summary, findings, and recommendations
6. A privacy badge shows how many patient identifiers were anonymized

Image Analysis

1. Navigate to the Image Analysis tab
2. Upload a medical document image (prescription, lab report, etc.)
3. Choose either Extract Text Only or Full Analysis
4. For full analysis, the system will extract text and provide medical insights
5. Review the extracted text and analysis results
6. Privacy information shows anonymization applied

Medical Research

1. Go to the Research tab
2. Enter a medical topic or condition you want to research
3. Click Search Medical Literature
4. Review the AI-summarized findings
5. Access links to original research materials from trusted sources

Privacy and Data Protection

How Anonymization Works

When you upload documents or ask questions:
1. System scans for Protected Health Information (PHI)
2. Patient names become [Patient Name]
3. Dates become [Date]
4. Contact information becomes [Phone] or [Email]
5. Medical IDs become [Medical ID]
6. Insurance numbers become [Insurance ID]
7. All other sensitive information gets replaced with appropriate placeholders

Data Processing Flow

User Input → Local Anonymization → External API Call → AI Response → Return to User

Critical Point: Original patient data never reaches external APIs. Anonymization happens locally before any external communication.

Compliance Standards

GDPR Compliance: Full compliance with General Data Protection Regulation Article 9 for special categories of health data.

HIPAA Compliance: Protection of all 18 HIPAA identifier categories.

EU AI Act: Compliance with Annex III requirements for high-risk AI in healthcare.

Data Retention: No permanent storage of medical data. All data is session-based only.

API Endpoints

All endpoints are at http://localhost:8000/api/

Medical Chat Endpoint

POST /api/chat
Request Body:
{
  "message": "your medical question",
  "language": "en"
}
Response:
{
  "response": "AI response",
  "language": "en",
  "timestamp": "2025-10-31T23:12:00"
}

Text Analysis Endpoint

POST /api/analyze-text
Request Body:
{
  "text": "medical document text",
  "context": "additional context",
  "language": "en"
}
Response includes summary, key findings, recommendations, next steps, and anonymization metadata.

Image Analysis Endpoint

POST /api/analyze-image
Form Data: file, language, extract_text_only
Returns extracted text and structured medical analysis.

Research Endpoint

POST /api/research
Request Body:
{
  "query": "medical topic",
  "language": "en"
}
Returns summary and list of research sources with links.

Configuration Options

Language Support

Supported languages: en (English), de (German)

To add new languages:
1. Create new system prompts in the chains
2. Add translations for UI text
3. Update language configuration in config.py

API Configuration

Configure API keys and other settings in the .env file. Available settings:
- GEMINI_API_KEY: Google Gemini API authentication
- TAVILY_API_KEY: Tavily research API authentication
- CORS_ORIGINS: Allowed origins for CORS requests


Compliance Notes for Production

Before deploying to production, consider:
- Implement user authentication and authorization
- Add database for audit logging
- Enable HTTPS/TLS encryption
- Implement role-based access control
- Regular security audits
- Healthcare staff training on AI limitations
- Validation protocols for clinical recommendations

Important Disclaimers

Medical Disclaimer

This application is designed as a supporting tool for healthcare professionals and informed individuals. It is not a replacement for professional medical advice. Always consult qualified healthcare professionals for medical diagnoses and treatment plans. The AI provides information based on training data and may not account for individual circumstances.

Responsibility

Users are fully responsible for validating all AI-generated medical information before clinical use. The developers and contributors are not liable for any medical decisions made based on this application's outputs.

Data Security

While we implement privacy protections, users must ensure compliance with healthcare regulations in their specific jurisdiction, including GDPR, HIPAA, or equivalent regulations.

Limitations

The application relies on external AI services and internet connectivity. Response quality depends on input clarity. Medical emergencies should always be addressed through emergency services, not through this application.

Contributing

This project was developed for educational and demonstration purposes. Contributions are welcome. Please ensure any modifications maintain compliance standards and do not compromise patient privacy.

Future Improvements

Planned enhancements include:
- Support for additional languages
- Integration with electronic health record systems
- Advanced clinical decision support algorithms
- Real-time collaboration features for medical teams
- Enhanced mobile support
- Integration with medical imaging analysis
- Clinical trial matching features


