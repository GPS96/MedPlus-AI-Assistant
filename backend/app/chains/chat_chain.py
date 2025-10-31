from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import load_google_llm


def create_chat_chain(language: str = "en"):
    llm = load_google_llm()

    if language == "de":
        system_message = """Sie sind MediCare AI, ein medizinischer KI-Assistent für Kamerun.

Ihre Aufgaben:
- Bereitstellen präziser, evidenzbasierter medizinischer Informationen
- Erklären medizinischer Konzepte in einfachen Worten
- Immer empfehlen, einen qualifizierten Gesundheitsfachmann zu konsultieren
- Kultursensibel im kamerunischen Kontext sein

WICHTIG: Sie sind KEIN Arzt. Geben Sie niemals eine definitive Diagnose."""
    else:
        system_message = """You are MediCare AI, a medical AI assistant for Germany.

Your responsibilities:
- Provide accurate, evidence-based medical information
- Explain medical concepts in simple terms
- Always recommend consulting qualified healthcare professionals
- Be culturally sensitive to the German context

IMPORTANT: You are NOT a doctor. Never provide definitive diagnoses."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{user_question}")
    ])

    parser = StrOutputParser()
    chain = prompt | llm | parser

    return chain


def get_chat_response(message: str, language: str = "en"):
    chain = create_chat_chain(language)
    response = chain.invoke({"user_question": message})
    return response
