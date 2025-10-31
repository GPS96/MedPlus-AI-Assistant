import streamlit as st
import requests
import base64
from PIL import Image
import io

# Configuration
FASTAPI_URL = "http://localhost:8000"  # Your FastAPI server

# Page configuration
st.set_page_config(
    page_title="MediCare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #546E7A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .success-box {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .privacy-badge {
        display: inline-block;
        background-color: #E8F5E9;
        border: 1px solid #4CAF50;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #2E7D32;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ← NEW: Add formatting function for anonymized text
def format_anonymized_text(text):
    """
    Make anonymization placeholders more readable and visually distinct.
    Converts <PLACEHOLDER> to formatted [Placeholder Name] format.
    """
    replacements = {
        '<PATIENT>': '**[Patient Name]**',
        '<DATE>': '**[Date]**',
        '<PHONE>': '**[Phone]**',
        '<EMAIL>': '**[Email]**',
        '<LOCATION>': '**[Address]**',
        '<MRN>': '**[Medical ID]**',
        '<DOC_ID>': '**[Document ID]**',
        '<LAB_ID>': '**[Lab ID]**',
    }
    
    formatted_text = text
    for placeholder, readable in replacements.items():
        formatted_text = formatted_text.replace(placeholder, readable)
    
    return formatted_text


# Header
st.markdown('<div class="main-header">🏥 MediCare AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Medical Document Analysis & Health Consultation</div>', unsafe_allow_html=True)

# Sidebar for language selection
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2913/2913133.png", width=100)
    st.title("Settings")
    
    language = st.selectbox(
        "Select Language / Sprache wählen",
        options=["en", "de"],
        format_func=lambda x: "🇬🇧 English" if x == "en" else "🇩🇪 Deutsch"
    )
    
    st.divider()
    
    st.info("**Features:**\n- 💬 Medical Chat\n- 📄 Document Analysis\n- 🖼️ Image Analysis\n- 📚 Research Search")
    
    st.divider()
    st.caption("⚠️ **Disclaimer:** This is an AI assistant, not a replacement for professional medical advice.")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Document Analysis", "🖼️ Image Analysis", "📚 Research"])

# TAB 1: Chat Interface
# TAB 1: Chat Interface
with tab1:
    st.header("Medical Consultation Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your medical question..." if language == "en" else "Stellen Sie Ihre medizinische Frage..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..." if language == "en" else "Denke nach..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/api/chat",
                        json={"message": prompt, "language": language}  # ← SEND ORIGINAL, NOT ANONYMIZED
                    )
                    
                    if response.status_code == 200:
                        ai_response = response.json()["response"]
                        # Don't anonymize chat responses - they're not sensitive
                        st.markdown(ai_response)  # ← REMOVE format_anonymized_text()
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    else:
                        st.error("Error connecting to AI service")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")


# TAB 2: Document Analysis (Text)
with tab2:
    st.header("Medical Document Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        medical_text = st.text_area(
            "Paste medical record text here:" if language == "en" else "Fügen Sie hier den Text der medizinischen Akte ein:",
            height=300,
            placeholder="Patient name: John Doe\nDate: 2025-10-30\nDiagnosis: ..." if language == "en" else "Patientenname: Max Mustermann\nDatum: 30.10.2025\nDiagnose: ..."
        )
        
        context = st.text_input(
            "Additional context (optional):" if language == "en" else "Zusätzlicher Kontext (optional):",
            placeholder="Patient history, current symptoms..." if language == "en" else "Krankengeschichte, aktuelle Symptome..."
        )
    
    with col2:
        st.info("**Analysis includes:**\n- Summary\n- Key Findings\n- Recommendations\n- Next Steps")
    
    if st.button("🔍 Analyze Document" if language == "en" else "🔍 Dokument analysieren", use_container_width=True):
        if medical_text:
            with st.spinner("Analyzing..." if language == "en" else "Analysiere..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/api/analyze-text",
                        json={
                            "text": medical_text,
                            "context": context,
                            "language": language
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Analysis Complete!" if language == "en" else "✅ Analyse abgeschlossen!")
                        
                        # ← NEW: Show privacy badge
                        if "privacy_metadata" in result and result["privacy_metadata"]:
                            privacy_data = result["privacy_metadata"]
                            if privacy_data.get("anonymization_applied"):
                                st.markdown(
                                    f'<div class="privacy-badge">🔒 Privacy Protected: {privacy_data.get("total_entities_anonymized", 0)} identifiers anonymized</div>',
                                    unsafe_allow_html=True
                                )
                        
                        # Summary
                        st.markdown("### 📊 Summary")
                        formatted_summary = format_anonymized_text(result.get("summary", "N/A"))
                        st.info(formatted_summary)
                        
                        # Key Findings - ← CHANGED: Apply formatting
                        st.markdown("### 🔬 Key Findings")
                        findings = result.get("key_findings", [])
                        if findings:
                            for finding in findings:
                                formatted_finding = format_anonymized_text(finding)
                                st.markdown(f"- {formatted_finding}")
                        else:
                            st.write("No key findings identified")
                        
                        # Recommendations - ← CHANGED: Apply formatting
                        st.markdown("### 💡 Recommendations")
                        recommendations = result.get("recommendations", [])
                        if recommendations:
                            for rec in recommendations:
                                formatted_rec = format_anonymized_text(rec)
                                st.markdown(f"- {formatted_rec}")
                        else:
                            st.write("No recommendations available")
                        
                        # Next Steps - ← CHANGED: Apply formatting
                        st.markdown("### 📋 Next Steps")
                        next_steps = result.get("next_steps", [])
                        if next_steps:
                            for step in next_steps:
                                formatted_step = format_anonymized_text(step)
                                st.markdown(f"✓ {formatted_step}")
                        else:
                            st.write("No next steps specified")
                        
                        # Disclaimer
                        st.markdown("---")
                        st.caption(f"⚠️ {result.get('disclaimer', '')}")
                    
                    else:
                        st.error("Analysis failed. Please try again.")
                        st.error(f"Details: {response.text}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter medical text to analyze" if language == "en" else "Bitte geben Sie medizinischen Text ein")

# TAB 3: Image Analysis
with tab3:
    st.header("Medical Image & Lab Report Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload medical document image (Lab report, prescription, etc.)" if language == "en" else "Medizinisches Dokument hochladen (Laborbericht, Rezept, etc.)",
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document", use_column_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Extract Text Only" if language == "en" else "📝 Nur Text extrahieren", use_container_width=True):
                with st.spinner("Extracting..." if language == "en" else "Extrahiere..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        response = requests.post(
                            f"{FASTAPI_URL}/api/extract-text",
                            files=files
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            extracted_text = result["extracted_text"]
                            st.success("✅ Text Extracted!" if language == "en" else "✅ Text extrahiert!")
                            
                            # ← NEW: Show privacy badge
                            if "entities_anonymized" in result:
                                st.markdown(
                                    f'<div class="privacy-badge">🔒 {result.get("entities_anonymized", 0)} identifiers anonymized</div>',
                                    unsafe_allow_html=True
                                )
                            
                            # ← NEW: Format extracted text
                            formatted_extracted = format_anonymized_text(extracted_text)
                            st.text_area("Extracted Text:", formatted_extracted, height=300)
                        else:
                            st.error(f"Extraction failed: {response.status_code}")
                            st.error(f"Details: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("🔍 Full Analysis" if language == "en" else "🔍 Vollständige Analyse", use_container_width=True):
                with st.spinner("Analyzing image..." if language == "en" else "Analysiere Bild..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"language": language, "extract_text_only": "false"}
                        
                        response = requests.post(
                            f"{FASTAPI_URL}/api/analyze-image",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            analysis = result.get("analysis", {})
                            extracted_text = result.get("extracted_text", "")
                            
                            st.success("✅ Analysis Complete!" if language == "en" else "✅ Analyse abgeschlossen!")
                            
                            # ← NEW: Show privacy badge
                            if "analysis" in result and "privacy_metadata" in result["analysis"]:
                                privacy_data = result["analysis"]["privacy_metadata"]
                                if privacy_data and privacy_data.get("anonymization_applied"):
                                    st.markdown(
                                        f'<div class="privacy-badge">🔒 Privacy Protected: {privacy_data.get("total_entities_anonymized", 0)} identifiers anonymized</div>',
                                        unsafe_allow_html=True
                                    )
                            
                            # Show extracted text in expander
                            if extracted_text:
                                with st.expander("📄 Extracted Text"):
                                    formatted_extracted = format_anonymized_text(extracted_text)
                                    st.text_area("", formatted_extracted, height=200)
                            
                            # Display analysis results
                            st.markdown("### 📊 Medical Analysis")
                            
                            # Summary
                            st.markdown("#### Summary")
                            formatted_summary = format_anonymized_text(analysis.get("summary", "No summary available"))
                            st.info(formatted_summary)
                            
                            # Key Findings - ← CHANGED: Apply formatting
                            st.markdown("#### 🔬 Key Findings")
                            findings = analysis.get("key_findings", [])
                            if findings:
                                for finding in findings:
                                    formatted_finding = format_anonymized_text(finding)
                                    st.markdown(f"- {formatted_finding}")
                            else:
                                st.write("No key findings identified")
                            
                            # Recommendations - ← CHANGED: Apply formatting
                            st.markdown("#### 💡 Recommendations")
                            recommendations = analysis.get("recommendations", [])
                            if recommendations:
                                for rec in recommendations:
                                    formatted_rec = format_anonymized_text(rec)
                                    st.markdown(f"- {formatted_rec}")
                            else:
                                st.write("No recommendations available")
                            
                            # Next Steps - ← CHANGED: Apply formatting
                            st.markdown("#### 📋 Next Steps")
                            next_steps = analysis.get("next_steps", [])
                            if next_steps:
                                for step in next_steps:
                                    formatted_step = format_anonymized_text(step)
                                    st.markdown(f"✓ {formatted_step}")
                            else:
                                st.write("No next steps specified")
                            
                            # Disclaimer
                            st.markdown("---")
                            st.caption(f"⚠️ {analysis.get('disclaimer', '')}")
                        
                        else:
                            st.error(f"Analysis failed: {response.status_code}")
                            st.error(f"Response: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())

# TAB 4: Medical Research
with tab4:
    st.header("Medical Research Search")
    
    research_query = st.text_input(
        "Enter medical topic or condition:" if language == "en" else "Medizinisches Thema oder Erkrankung eingeben:",
        placeholder="e.g., diabetes management, hypertension treatment" if language == "en" else "z.B. Diabetesmanagement, Bluthochdruckbehandlung"
    )
    
    if st.button("🔬 Search Medical Literature" if language == "en" else "🔬 Medizinische Literatur durchsuchen", use_container_width=True):
        if research_query:
            with st.spinner("Searching..." if language == "en" else "Suche..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/api/research",
                        json={"query": research_query, "language": language}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Research Complete!" if language == "en" else "✅ Recherche abgeschlossen!")
                        
                        # Summary
                        st.markdown("### 📊 Summary")
                        formatted_summary = format_anonymized_text(result.get("summary", "No summary available"))
                        st.info(formatted_summary)
                        
                        # Sources
                        if "sources" in result:
                            st.markdown("### 📚 Sources")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(f"Source {i}: {source.get('title', 'Untitled')}"):
                                    st.markdown(f"**URL:** {source.get('url', 'N/A')}")
                                    formatted_content = format_anonymized_text(source.get('content', 'No content available'))
                                    st.markdown(formatted_content)
                    
                    else:
                        st.error("Research failed")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a research query" if language == "en" else "Bitte geben Sie eine Suchanfrage ein")

# Footer
st.divider()
st.caption("🏥 MedPlus AI | Powered by Google Gemini 2.5 & LangChain")
