from datetime import datetime, timedelta
from typing import Dict

from faker import Faker

from models import PIIDetection


class PIIReplacer:
    """Generates consistent synthetic replacements for detected PII."""

    def __init__(self) -> None:
        self.faker = Faker("en_IN")
        self._replacements: Dict[str, str] = {}

    def replace(self, detection: PIIDetection) -> str:
        key = f"{detection.entity_type}:{detection.value}"

        if key not in self._replacements:
            self._replacements[key] = self._generate_replacement(
                detection
            )

        return self._replacements[key]

    def _generate_replacement(
        self,
        detection: PIIDetection,
    ) -> str:

        generators = {
            "PERSON": self.faker.name,
            "EMAIL_ADDRESS": self.faker.email,
            "PHONE_NUMBER": self._fake_phone,
            "ORGANIZATION": self.faker.company,
            "ADDRESS": self.faker.address,
            "IP_ADDRESS": self.faker.ipv4,
            "CREDIT_CARD": self.faker.credit_card_number,
            "US_SSN": self.faker.ssn,
            "DATE_OF_BIRTH": self._fake_date,
        }

        generator = generators.get(detection.entity_type)

        if generator is None:
            return "[REDACTED]"

        return generator()

    def _fake_phone(self) -> str:
        return f"+91 {self.faker.msisdn()[3:]}"

    def _fake_date(self) -> str:
        start = datetime(1970, 1, 1)
        end = datetime(2000, 12, 31)

        date = self.faker.date_between(
            start_date=start,
            end_date=end,
        )

        return date.strftime("%d/%m/%Y")