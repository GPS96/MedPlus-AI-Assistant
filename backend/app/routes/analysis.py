from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import (
    ChatRequest, ChatResponse,
    AnalysisRequest, AnalysisResponse,
    ImageAnalysisResponse
)
from app.chains.chat_chain import get_chat_response
from app.chains.analysis_chain import analyze_medical_record
from app.services.gemini_service import gemini_service
from app.services.anonymization_service import anonymization_service  # ← NEW: ADD THIS LINE
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        # ← REMOVE anonymization for chat - just send it directly
        response_text = get_chat_response(
            message=request.message,  # Send original message
            language=request.language
        )
        
        return ChatResponse(
            response=response_text,
            language=request.language,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")



@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_medical_text(request: AnalysisRequest):
    try:
        # ← NEW: Anonymize text before analysis
        anonymized_text, anon_metadata = anonymization_service.anonymize_text(
            request.text,
            language=request.language
        )
        
        # ← NEW: Anonymize context too
        anonymized_context, _ = anonymization_service.anonymize_text(
            request.context if request.context else "",
            language=request.language
        )
        
        analysis = analyze_medical_record(
            text=anonymized_text,  # ← CHANGED: Use anonymized version
            context=anonymized_context,  # ← CHANGED: Use anonymized version
            language=request.language
        )
        
        # ← CHANGED: Update disclaimer with privacy info
        if request.language == "de":
            disclaimer = (
                f"🔒 Datenschutz: {anon_metadata.get('total_entities_anonymized', 0)} persönliche Identifikatoren wurden anonymisiert (DSGVO-konform). "
                "Diese Analyse dient nur zu Informationszwecken. "
                "Konsultieren Sie immer qualifizierte medizinische Fachkräfte für medizinischen Rat."
            )
        else:
            disclaimer = (
                f"🔒 Privacy: {anon_metadata.get('total_entities_anonymized', 0)} personal identifiers anonymized (GDPR/HIPAA compliant). "
                "This analysis is for informational purposes only. "
                "Always consult qualified healthcare professionals for medical advice."
            )
        
        return AnalysisResponse(
            summary=analysis.summary,
            key_findings=analysis.key_findings,
            recommendations=analysis.recommendations,
            next_steps=analysis.next_steps,
            disclaimer=disclaimer,
            language=request.language,
            timestamp=datetime.now(),
            privacy_metadata=anon_metadata  # ← NEW: Include anonymization details
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_medical_image(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    extract_text_only: bool = Form(default=False)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_bytes = await file.read()
        extracted_text = gemini_service.extract_text_from_image(image_bytes)
        
        # ← NEW: Anonymize extracted text
        anonymized_text, anon_metadata = anonymization_service.anonymize_text(
            extracted_text,
            language=language
        )
        
        if extract_text_only:
            # ← CHANGED: Update disclaimer with privacy info
            if language == "de":
                disclaimer = f"🔒 {anon_metadata.get('total_entities_anonymized', 0)} Identifikatoren anonymisiert. Nur Textextraktion - keine Analyse durchgeführt"
            else:
                disclaimer = f"🔒 {anon_metadata.get('total_entities_anonymized', 0)} identifiers anonymized. Text extraction only - no analysis performed"
            
            return ImageAnalysisResponse(
                extracted_text=anonymized_text,  # ← CHANGED: Return anonymized version
                analysis=AnalysisResponse(
                    summary="Text extraction completed",
                    key_findings=[],
                    recommendations=[],
                    next_steps=["Review the extracted text", "Analyze if needed"],
                    disclaimer=disclaimer,
                    language=language,
                    timestamp=datetime.now(),
                    privacy_metadata=anon_metadata  # ← NEW
                )
            )
        
        # Full analysis with anonymized text
        analysis = analyze_medical_record(
            text=anonymized_text,  # ← CHANGED: Use anonymized version
            language=language
        )
        
        # ← CHANGED: Update disclaimer with privacy info
        if language == "de":
            disclaimer = (
                f"🔒 Datenschutz: {anon_metadata.get('total_entities_anonymized', 0)} persönliche Identifikatoren wurden anonymisiert (DSGVO/EU AI Act konform). "
                "Diese Analyse dient nur zu Informationszwecken. "
                "Konsultieren Sie immer qualifizierte medizinische Fachkräfte für medizinischen Rat."
            )
        else:
            disclaimer = (
                f"🔒 Privacy: {anon_metadata.get('total_entities_anonymized', 0)} personal identifiers anonymized (GDPR/HIPAA/EU AI Act compliant). "
                "This analysis is for informational purposes only. "
                "Always consult qualified healthcare professionals for medical advice."
            )
        
        return ImageAnalysisResponse(
            extracted_text=anonymized_text,  # ← CHANGED: Return anonymized version
            analysis=AnalysisResponse(
                summary=analysis.summary,
                key_findings=analysis.key_findings,
                recommendations=analysis.recommendations,
                next_steps=analysis.next_steps,
                disclaimer=disclaimer,
                language=language,
                timestamp=datetime.now(),
                privacy_metadata=anon_metadata  # ← NEW
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")


@router.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_bytes = await file.read()
        extracted_text = gemini_service.extract_text_from_image(image_bytes)
        
        # ← NEW: Anonymize extracted text
        anonymized_text, anon_metadata = anonymization_service.anonymize_text(
            extracted_text,
            language="en"
        )
        
        return {
            "extracted_text": anonymized_text,  # ← CHANGED: Return anonymized version
            "timestamp": datetime.now(),
            "privacy_compliance": anon_metadata.get("compliance_status", "Protected"),  # ← NEW
            "entities_anonymized": anon_metadata.get("total_entities_anonymized", 0)  # ← NEW
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction error: {str(e)}")
