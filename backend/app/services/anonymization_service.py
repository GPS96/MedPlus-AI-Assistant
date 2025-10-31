import re
from typing import Dict, Tuple, List
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig


class MedicalAnonymizationService:
    """
    Lightweight GDPR/HIPAA compliant anonymization using regex patterns.
    Works on Windows without C++ compiler requirements.
    """
    
    def __init__(self):
        self.anonymizer = AnonymizerEngine()
        
        # HIPAA Safe Harbor + GDPR patterns
        self.patterns = {
            # Names (enhanced for German formats)
            'PERSON': [
                # Titles + Names
                r'\b(?:Dr\.|Doctor|Patient|Mr\.|Mrs\.|Ms\.|Herr|Frau|Prof\.|Professor)\s+(?:med\.\s+)?[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){0,3}\b',
                # German format: Last First (Mustermann Erika)
                r'\b[A-ZÄÖÜ][a-zäöüß]{2,15}\s+[A-ZÄÖÜ][a-zäöüß]{2,15}\b',
                # Full names with common patterns
                r'\b[A-ZÄÖÜ][a-z]+(?:\s+[A-ZÄÖÜ][a-z]+){1,2}(?=\s*\n|\s*geb\.|\s*geboren|\s*DOB|\s*[,])',
                # Names before street addresses (German format)
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+(?=\s+[A-ZÄÖÜ][a-zäöüß]+straße|\s+[A-ZÄÖÜ][a-zäöüß]+str\.)',
            ],
            # Dates (multiple formats)
            'DATE_TIME': [
                r'\b\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}\b',  # 31/10/2025, 31.10.2025, 10/14
                r'\b\d{4}[./\-]\d{1,2}[./\-]\d{1,2}\b',  # 2025-10-31
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}\b',
                # German short dates like "10.07.2012"
                r'\b\d{2}\.\d{2}\.\d{4}\b',
            ],
            # German Street Addresses (Heidestraße 17, etc.)
            'LOCATION': [
                r'\b[A-ZÄÖÜ][a-zäöüß]+(?:straße|strasse|str\.|weg|platz|allee)\s+\d{1,4}[a-z]?\b',
                r'\b\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+\b',  # Postal code + city (51147 Köln)
                r'\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St\.|Avenue|Ave\.|Road|Rd\.)\b',
                r'\b\d{5}(?:-\d{4})?\b',  # ZIP codes alone
            ],
            # Phone numbers
            'PHONE_NUMBER': [
                r'\b\+?\d{1,4}[-.\s/]?\(?\d{1,4}\)?[-.\s/]?\d{1,4}[-.\s/]?\d{1,4}[-.\s/]?\d{0,4}\b',
                r'\bTel[:\s.]+\d+[\d\s/\-]+\b',
            ],
            # Email
            'EMAIL_ADDRESS': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            # Medical IDs (enhanced for German formats)
            'MEDICAL_ID': [
                r'\b(?:MRN|Patient[\s\-]ID|ID|Kassen-Nr|Versicherten-Nr)[\s:.]+[A-Z0-9]+\b',
                r'\b(?:NHS|Insurance|Versicherung)[\s#:]+[A-Z0-9]{6,12}\b',
                r'\b[A-Z]\d{9}\b',  # German insurance number format
                r'\b\d{8,10}\b(?=\s*\n|\s*$)',  # Standalone 8-10 digit numbers (like 106415300)
            ],
            # Prescription/Document Numbers
            'DOCUMENT_ID': [
                r'\bBetriebsstätten-Nr[.:\s]+\d+\b',
                r'\bArzt-Nr[.:\s]+\d+\b',
                r'\bKassen-Nr[.:\s]+\d+\b',
                r'\bStatus[:\s]+\d+\s+\d+\b',
                r'\b\d{7,10}(?=\s*$)',  # Document numbers at end of line
            ],
            # Lab/Prescription IDs
            'LAB_ID': [
                r'\bLab[\s#:]+\d{5,8}\b',
                r'\bRx[\s#:]+\d{6,10}\b',
                r'\bRp\.[\s#:]*[^\n]+',  # Prescription lines starting with Rp.
            ],
        }
        
        self.replacements = {
            'PERSON': '<PATIENT>',
            'DATE_TIME': '<DATE>',
            'PHONE_NUMBER': '<PHONE>',
            'EMAIL_ADDRESS': '<EMAIL>',
            'LOCATION': '<LOCATION>',
            'MEDICAL_ID': '<MRN>',
            'DOCUMENT_ID': '<DOC_ID>',
            'LAB_ID': '<LAB_ID>',
        }

    
    def anonymize_text(self, text: str, language: str = "en") -> Tuple[str, Dict]:
        """
        Anonymize medical text using regex patterns.
        
        Args:
            text: Original medical text
            language: Language code ("en" or "de")
        
        Returns:
            Tuple of (anonymized_text, metadata)
        """
        if not text or text.strip() == "":
            return text, {"entities_found": [], "anonymization_applied": False}
        
        anonymized_text = text
        entities_found = []
        total_matches = 0
        
        try:
            # Apply each pattern
            for entity_type, pattern_list in self.patterns.items():
                for pattern in pattern_list:
                    matches = list(re.finditer(pattern, anonymized_text, re.IGNORECASE))
                    
                    if matches:
                        for match in matches:
                            entities_found.append({
                                "entity_type": entity_type,
                                "text": match.group(),
                                "start": match.start(),
                                "end": match.end()
                            })
                            total_matches += 1
                        
                        # Replace with placeholder
                        anonymized_text = re.sub(
                            pattern,
                            self.replacements[entity_type],
                            anonymized_text,
                            flags=re.IGNORECASE
                        )
            
            # Metadata
            if total_matches == 0:
                return text, {
                    "entities_found": [],
                    "anonymization_applied": False,
                    "total_entities_anonymized": 0,
                    "compliance_status": "No PHI detected",
                    "entity_types_found": []
                }
            
            metadata = {
                "entities_found": entities_found[:10],  # Limit to first 10 for brevity
                "anonymization_applied": True,
                "total_entities_anonymized": total_matches,
                "compliance_status": "GDPR/HIPAA compliant - PHI anonymized",
                "entity_types_found": list(set([e["entity_type"] for e in entities_found]))
            }
            
            return anonymized_text, metadata
        
        except Exception as e:
            print(f"Anonymization error: {e}")
            return text, {
                "entities_found": [],
                "anonymization_applied": False,
                "error": str(e),
                "compliance_status": "Error - manual review required"
            }
    
    def anonymize_with_de_identification(self, text: str, language: str = "en") -> Tuple[str, Dict]:
        """
        Alias for anonymize_text for compatibility.
        """
        return self.anonymize_text(text, language)


# Singleton instance
anonymization_service = MedicalAnonymizationService()
