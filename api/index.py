import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from detection.engine import DetectionEngine
from document.writer import DocumentWriter
from redaction.service import RedactionService
from replacement.replacer import PIIReplacer


app = FastAPI(
    title="PII Redaction Tool",
    description="API for detecting and redacting PII from DOCX documents.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "PII Redaction Tool API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/redact")
async def redact_document(
    file: UploadFile = File(...)
):
    if not file.filename:
        return {
            "error": "No file provided."
        }

    if not file.filename.lower().endswith(".docx"):
        return {
            "error": "Only DOCX files are supported."
        }

    input_file = None
    output_file = None

    try:
        input_file = NamedTemporaryFile(
            suffix=".docx",
            delete=False,
        )

        input_file.write(
            await file.read()
        )

        input_file.close()

        output_file = NamedTemporaryFile(
            suffix=".docx",
            delete=False,
        )

        output_file.close()

        detector = DetectionEngine()
        replacer = PIIReplacer()

        service = RedactionService(
            detector=detector,
            replacer=replacer,
        )

        writer = DocumentWriter()

        def redact_text(text: str) -> str:
            redacted, _ = service.redact(text)
            return redacted

        writer.write(
            input_path=Path(input_file.name),
            output_path=Path(output_file.name),
            redact_text=redact_text,
        )

        return FileResponse(
            path=output_file.name,
            filename="redacted_document.docx",
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
        )

    except Exception as exc:
        return {
            "error": str(exc)
        }