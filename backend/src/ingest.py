"""Extract text page-by-page and retain provenance before splitting."""

from hashlib import sha256
from io import BytesIO
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def parse_pdf(data: bytes, filename: str, settings):
    if not data or len(data) > settings.max_pdf_mb * 1024 * 1024:
        raise ValueError(f"PDF must be nonempty and at most {settings.max_pdf_mb} MB.")
    if not data.lstrip().startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a PDF.")
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported. Upload an unlocked copy.")
        if len(reader.pages) > 500:
            raise ValueError("Limit: 500 pages per PDF.")
        doc_id = sha256(data).hexdigest()
        name = Path(filename.replace("\\", "/")).name
        pages, skipped = [], []
        for number, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(
                    Document(
                        page_content=text,
                        metadata={
                            "doc_id": doc_id,
                            "filename": name,
                            "page": number,
                        },
                    )
                )
            else:
                skipped.append(number)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Cannot read this PDF. It may be damaged.") from exc
    if not pages:
        raise ValueError("No extractable text. Run OCR on scanned PDFs first.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        add_start_index=True,
    )
    chunks = splitter.split_documents(pages)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{doc_id}:{index}"
    return doc_id, chunks, skipped
