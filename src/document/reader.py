from pathlib import Path

from docx import Document


class DocumentReader:
    """Reads text content from a DOCX document."""

    def read(self, file_path: Path) -> str:
        document = Document("C:\\Users\\yvsya\\OneDrive\\Desktop\\PII_redaction\\input\\Red Herring Prospectus.docx")

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)