from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.config import load_google_llm
from app.models.schemas import MedicalAnalysis


def create_analysis_chain(language: str = "en"):
    llm = load_google_llm()
    parser = PydanticOutputParser(pydantic_object=MedicalAnalysis)
    format_instructions = parser.get_format_instructions()

    if language == "de":
        system_message = """Sie sind ein medizinischer KI-Assistent, der medizinische Unterlagen analysiert.
Geben Sie klare, präzise und umsetzbare Informationen.
Bleiben Sie objektiv und empfehlen Sie immer eine professionelle medizinische Beratung.

WICHTIG: Antworten Sie AUSSCHLIESSLICH auf Deutsch. Alle Felder müssen in deutscher Sprache sein."""

        user_template = """Analysieren Sie diese medizinische Akte und liefern Sie eine strukturierte Analyse AUF DEUTSCH:

Medizinische Akte:
{medical_text}

Zusätzlicher Kontext:
{context}

{format_instructions}

KRITISCHE ANWEISUNG: 
- Schreiben Sie ALLE Texte auf Deutsch
- summary (Zusammenfassung) = auf Deutsch
- key_findings (Wichtige Befunde) = auf Deutsch
- recommendations (Empfehlungen) = auf Deutsch
- next_steps (Nächste Schritte) = auf Deutsch
- patient_summary (Patienten-Zusammenfassung) = auf Deutsch in einfacher Sprache
- technical_notes (Technische Notizen) = auf Deutsch für Ärzte
- reasoning (Begründung) = auf Deutsch

Antworten Sie NUR mit gültigem JSON. Der gesamte Inhalt muss in deutscher Sprache sein."""
    else:
        system_message = """You are a medical AI assistant analyzing medical records.
Provide clear, accurate, and actionable insights.
Stay objective and always recommend professional medical consultation.

IMPORTANT: Respond EXCLUSIVELY in English. All fields must be in English language."""

        user_template = """Analyze this medical record and provide a structured analysis IN ENGLISH:

Medical Record:
{medical_text}

Additional Context:
{context}

{format_instructions}

CRITICAL INSTRUCTION:
- Write ALL text in English
- summary = in English
- key_findings = in English
- recommendations = in English
- next_steps = in English
- patient_summary = in simple English for patients
- technical_notes = in English for doctors
- reasoning = in English

Respond ONLY with valid JSON. All content must be in English language."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", user_template)
    ])

    prompt = prompt.partial(format_instructions=format_instructions)
    chain = prompt | llm | parser

    return chain


def analyze_medical_record(text: str, context: str = "", language: str = "en"):
    chain = create_analysis_chain(language)

    try:
        result = chain.invoke({
            "medical_text": text,
            "context": context if context else "Kein zusätzlicher Kontext angegeben" if language == "de" else "No additional context provided"
        })
        return result
    except Exception as e:
        print(f"Analysis error: {e}")
        
        # Language-aware error fallback
        if language == "de":
            return MedicalAnalysis(
                summary=f"Analyse abgeschlossen, aber Formatierungsprobleme aufgetreten: {str(e)[:200]}",
                key_findings=["Analyse wurde durchgeführt, aber Ergebnisse benötigen manuelle Überprüfung"],
                recommendations=["Konsultieren Sie einen Arzt für detaillierte Interpretation"],
                next_steps=["Vereinbaren Sie einen Termin mit Ihrem Arzt", "Bewahren Sie diese Akte für Ihre Krankengeschichte auf"],
                patient_summary="Die Analyse konnte nicht vollständig abgeschlossen werden. Bitte konsultieren Sie einen Arzt.",
                technical_notes="Technische Fehler bei der Analyse. Manuelle Überprüfung erforderlich.",
                confidence_score=0.3,
                reasoning="Technischer Fehler während der Verarbeitung"
            )
        else:
            return MedicalAnalysis(
                summary=f"Analysis completed but encountered formatting issues: {str(e)[:200]}",
                key_findings=["Analysis was performed but results need manual review"],
                recommendations=["Consult with a healthcare professional for detailed interpretation"],
                next_steps=["Schedule appointment with your doctor", "Keep this record for your medical history"],
                patient_summary="The analysis could not be fully completed. Please consult a doctor.",
                technical_notes="Technical error during analysis. Manual review required.",
                confidence_score=0.3,
                reasoning="Technical error during processing"
            )
