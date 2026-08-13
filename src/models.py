from dataclasses import dataclass


@dataclass(frozen=True)
class PIIDetection:
    """Represents one detected PII value."""

    entity_type: str
    value: str
    start: int
    end: int
    score: float