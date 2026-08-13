import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from detection.engine import DetectionEngine
from document.writer import DocumentWriter
from redaction.service import RedactionService
from replacement.replacer import PIIReplacer


app = FastAPI(
    title="PII Redaction Tool",
    description="Detect and redact PII from DOCX documents.",
    version="1.0.0",
)


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PII Redaction Tool</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 700px;
            margin: 80px auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
        }

        h1 {
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }

        .upload-box {
            border: 2px dashed #aaa;
            padding: 35px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        input[type="file"] {
            margin: 15px;
        }

        button {
            background: #111827;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 7px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #374151;
        }

        .features {
            margin-top: 30px;
            color: #555;
            line-height: 1.8;
        }

        .footer {
            margin-top: 30px;
            font-size: 13px;
            color: #888;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>PII Redaction Tool</h1>

    <p class="subtitle">
        Detect and replace personally identifiable information
        from DOCX documents with synthetic values.
    </p>

    <form
        action="/api/redact"
        method="post"
        enctype="multipart/form-data"
    >

        <div class="upload-box">

            <strong>Upload a DOCX document</strong>

            <br>

            <input
                type="file"
                name="file"
                accept=".docx"
                required
            >

            <br>

            <button type="submit">
                Redact PII
            </button>

        </div>

    </form>

    <div class="features">

        <strong>Supported PII types</strong>

        <br>

        Names • Emails • Phone Numbers • Organizations
        • Addresses • SSNs • Credit Cards • DOB • IP Addresses

    </div>

    <div class="footer">

        Hybrid detection using Microsoft Presidio,
        custom rules and synthetic replacement.

    </div>

</div>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


@app.get("/health")
def health():
    return {
        "status": "healthy"
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

        content = await file.read()

        input_file.write(content)
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