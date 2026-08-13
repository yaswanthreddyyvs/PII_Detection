import re
from typing import List

from models import PIIDetection


class CustomDetector:
    """Detects PII using deterministic patterns and contextual rules."""

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+\s*91[\s-]?)?"
    r"(?:[6-9]\d{9}|\d{2,4}[\s-]?\d{6,8})"
    r"(?!\d)"
)

    IP_PATTERN = re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    )

    SSN_PATTERN = re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b"
    )

    CREDIT_CARD_PATTERN = re.compile(
        r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"
    )

    DATE_PATTERN = re.compile(
        r"\b(?:"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        r")\b"
    )

    COMPANY_PATTERN = re.compile(
        r"\b[A-Z][A-Za-z0-9&.,' -]{2,80}"
        r"(?:Limited|Ltd\.?|Private Limited|Pvt\.?\s*Ltd\.?|"
        r"Corporation|Corp\.?|Inc\.?|Industries|Technologies|"
        r"Enterprises|Holdings|Bank|Company)\b",
        re.IGNORECASE,
    )

    ADDRESS_CONTEXT_PATTERN = re.compile(
        r"(?i)\b(?:registered office|corporate office|"
        r"registered address|corporate address|"
        r"office address|residential address|"
        r"mailing address|correspondence address|"
        r"address)\s*[:\-]?\s*"
        r"(.{10,250}?(?:\b\d{6}\b|PIN\s*[:\-]?\s*\d{6}))"
    )

    def detect(self, text: str) -> List[PIIDetection]:
        detections: List[PIIDetection] = []

        detections.extend(
            self._find_matches(
                text,
                self.EMAIL_PATTERN,
                "EMAIL_ADDRESS",
            )
        )

        detections.extend(
            self._find_matches(
                text,
                self.PHONE_PATTERN,
                "PHONE_NUMBER",
            )
        )

        detections.extend(
            self._find_matches(
                text,
                self.IP_PATTERN,
                "IP_ADDRESS",
            )
        )

        detections.extend(
            self._find_matches(
                text,
                self.SSN_PATTERN,
                "US_SSN",
            )
        )

        detections.extend(self._detect_credit_cards(text))
        detections.extend(self._detect_dob(text))
        detections.extend(self._detect_companies(text))
        detections.extend(self._detect_addresses(text))

        return detections

    @staticmethod
    def _find_matches(
        text: str,
        pattern: re.Pattern[str],
        entity_type: str,
    ) -> List[PIIDetection]:

        return [
            PIIDetection(
                entity_type=entity_type,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                score=1.0,
            )
            for match in pattern.finditer(text)
        ]

    def _detect_credit_cards(
        self,
        text: str,
    ) -> List[PIIDetection]:

        detections = []

        for match in self.CREDIT_CARD_PATTERN.finditer(text):
            value = match.group()
            digits = re.sub(r"[- ]", "", value)

            if 13 <= len(digits) <= 19 and self._passes_luhn(digits):
                detections.append(
                    PIIDetection(
                        entity_type="CREDIT_CARD",
                        value=value,
                        start=match.start(),
                        end=match.end(),
                        score=1.0,
                    )
                )

        return detections

    def _detect_dob(
        self,
        text: str,
    ) -> List[PIIDetection]:

        detections = []

        pattern = re.compile(
            r"(?i)\b(?:date\s+of\s+birth|dob|"
            r"birth\s+date|born)\b"
            r".{0,40}?"
            r"(" + self.DATE_PATTERN.pattern + r")"
        )

        for match in pattern.finditer(text):
            start = match.start(1)
            end = match.end(1)

            detections.append(
                PIIDetection(
                    entity_type="DATE_OF_BIRTH",
                    value=match.group(1),
                    start=start,
                    end=end,
                    score=1.0,
                )
            )

        return detections

    def _detect_companies(
        self,
        text: str,
    ) -> List[PIIDetection]:

        detections = []

        for match in self.COMPANY_PATTERN.finditer(text):
            value = match.group().strip()

            if len(value) < 5:
                continue

            detections.append(
                PIIDetection(
                    entity_type="ORGANIZATION",
                    value=value,
                    start=match.start(),
                    end=match.end(),
                    score=0.85,
                )
            )

        return detections

    def _detect_addresses(
        self,
        text: str,
    ) -> List[PIIDetection]:

        detections = []

        for match in self.ADDRESS_CONTEXT_PATTERN.finditer(text):
            value = match.group(1).strip()

            start = match.start(1)
            end = match.end(1)

            detections.append(
                PIIDetection(
                    entity_type="ADDRESS",
                    value=value,
                    start=start,
                    end=end,
                    score=0.90,
                )
            )

        return detections

    @staticmethod
    def _passes_luhn(number: str) -> bool:
        total = 0
        reversed_digits = number[::-1]

        for index, digit in enumerate(reversed_digits):
            value = int(digit)

            if index % 2 == 1:
                value *= 2

                if value > 9:
                    value -= 9

            total += value

        return total % 10 == 0