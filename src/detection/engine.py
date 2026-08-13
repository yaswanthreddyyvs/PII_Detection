from typing import List

from detection.custom_detector import CustomDetector
from detection.detector import PIIDetector
from models import PIIDetection


class DetectionEngine:
    """Combines Presidio and custom PII detection."""

    def __init__(self) -> None:
        self.presidio_detector = PIIDetector()
        self.custom_detector = CustomDetector()

    def detect(self, text: str) -> List[PIIDetection]:
        detections = (
            self.presidio_detector.detect(text)
            + self.custom_detector.detect(text)
        )

        return self._merge_detections(detections)

    @staticmethod
    def _merge_detections(
        detections: List[PIIDetection],
    ) -> List[PIIDetection]:

        selected: List[PIIDetection] = []

        for detection in sorted(
            detections,
            key=lambda item: (
                item.start,
                -(item.end - item.start),
                -item.score,
            ),
        ):
            overlaps = any(
                detection.start < existing.end
                and detection.end > existing.start
                for existing in selected
            )

            if not overlaps:
                selected.append(detection)

        return sorted(
            selected,
            key=lambda item: item.start,
        )