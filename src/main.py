from pathlib import Path

from detection.engine import DetectionEngine
from document.reader import DocumentReader
from document.writer import DocumentWriter
from redaction.service import RedactionService
from replacement.replacer import PIIReplacer


INPUT_FILE = Path("input/Red Herring Prospectus.docx")
OUTPUT_FILE = Path("output/redacted_prospectus.docx")


def main() -> None:
    reader = DocumentReader()
    detector = DetectionEngine()
    replacer = PIIReplacer()

    service = RedactionService(
        detector=detector,
        replacer=replacer,
    )

    text = reader.read(INPUT_FILE)

    redacted_text, detections = service.redact(text)

    writer = DocumentWriter()

    def redact_document_text(value: str) -> str:
        redacted, _ = service.redact(value)
        return redacted

    writer.write(
        input_path=INPUT_FILE,
        output_path=OUTPUT_FILE,
        redact_text=redact_document_text,
    )

    print(f"Characters analyzed : {len(text):,}")
    print(f"PII detections      : {len(detections):,}")
    print(f"Output file         : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()