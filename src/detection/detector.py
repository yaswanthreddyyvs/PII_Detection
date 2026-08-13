from typing import List

from presidio_analyzer import AnalyzerEngine

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
        self.analyzer = AnalyzerEngine()

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