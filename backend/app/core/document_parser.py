# backend/app/core/document_parser.py
"""Document parsing for PDF and text files."""

from __future__ import annotations

import io
from typing import Optional

from app.core.observability import logs


class DocumentParser:
    """Parse documents to extract text."""

    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "text",
        "text/markdown": "text",
        "application/octet-stream": "auto",
    }

    async def parse(self, content: bytes, content_type: str, filename: str) -> str:
        """Parse document content to text."""
        try:
            file_type = self.SUPPORTED_TYPES.get(content_type, "auto")

            # Auto-detect from extension
            if file_type == "auto":
                if filename.lower().endswith(".pdf"):
                    file_type = "pdf"
                else:
                    file_type = "text"

            if file_type == "pdf":
                return await self._parse_pdf(content, filename)
            else:
                return self._parse_text(content, filename)

        except Exception as e:
            logs.error(f"Failed to parse document: {filename}", "parser", exception=e)
            # Fallback to raw text
            return content.decode("utf-8", errors="ignore")

    async def _parse_pdf(self, content: bytes, filename: str) -> str:
        """Extract text from PDF using pypdf."""
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        text = "\n\n".join(text_parts)

        logs.info(
            f"Parsed PDF: {filename}",
            "parser",
            metadata={"chars": len(text), "pages": len(reader.pages)},
        )

        return text

    def _parse_text(self, content: bytes, filename: str) -> str:
        """Parse text/markdown file."""
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="ignore")

        logs.info(
            f"Parsed text: {filename}",
            "parser",
            metadata={"chars": len(text)},
        )

        return text


_parser: Optional[DocumentParser] = None


def get_parser() -> DocumentParser:
    """Get document parser instance."""
    global _parser
    if _parser is None:
        _parser = DocumentParser()
    return _parser
