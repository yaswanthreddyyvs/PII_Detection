from typing import List

from detection.engine import DetectionEngine
from models import PIIDetection
from replacement.replacer import PIIReplacer


class RedactionService:
    """Detects PII and replaces it with synthetic values."""

    def __init__(
        self,
        detector: DetectionEngine,
        replacer: PIIReplacer,
    ) -> None:
        self.detector = detector
        self.replacer = replacer

    def redact(self, text: str) -> tuple[str, List[PIIDetection]]:
        detections = self.detector.detect(text)

        if not detections:
            return text, []

        redacted_parts = []
        cursor = 0

        for detection in detections:
            redacted_parts.append(text[cursor:detection.start])
            redacted_parts.append(self.replacer.replace(detection))
            cursor = detection.end

        redacted_parts.append(text[cursor:])

        return "".join(redacted_parts), detections