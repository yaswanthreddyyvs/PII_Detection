from typing import List

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from models import PIIDetection


class PIIDetector:
    """Detects relevant PII entities using Microsoft Presidio."""

    ALLOWED_ENTITIES = {
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "IP_ADDRESS",
        "CREDIT_CARD",
        "US_SSN",
        "ORGANIZATION",
    }

    MIN_CONFIDENCE = 0.70

    def __init__(self) -> None:
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "en",
                    "model_name": "en_core_web_sm",
                }
            ],
        }

        provider = NlpEngineProvider(
            nlp_configuration=configuration
        )

        nlp_engine = provider.create_engine()

        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"],
        )

    def detect(self, text: str) -> List[PIIDetection]:
        results = self.analyzer.analyze(
            text=text,
            language="en",
        )

        detections: List[PIIDetection] = []

        for result in results:
            if result.entity_type not in self.ALLOWED_ENTITIES:
                continue

            if result.score < self.MIN_CONFIDENCE:
                continue

            detections.append(
                PIIDetection(
                    entity_type=result.entity_type,
                    value=text[result.start:result.end],
                    start=result.start,
                    end=result.end,
                    score=result.score,
                )
            )

        return detections