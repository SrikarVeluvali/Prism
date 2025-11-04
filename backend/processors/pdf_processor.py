import PyPDF2
from typing import Any, Dict
from .base_processor import BaseProcessor


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents"""

    def extract_text(self, file_path_or_content: Any) -> str:
        """
        Extract all text content from a PDF file.

        Args:
            file_path_or_content: File-like object or path to PDF

        Returns:
            Concatenated text from all pages
        """
        pdf_reader = PyPDF2.PdfReader(file_path_or_content)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()

    def get_file_type(self) -> str:
        """Get the file type this processor handles"""
        return "pdf"

    def get_metadata(self, file_path_or_content: Any) -> Dict[str, Any]:
        """
        Extract metadata from PDF

        Args:
            file_path_or_content: File-like object or path to PDF

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            pdf_reader = PyPDF2.PdfReader(file_path_or_content)
            metadata = {
                "num_pages": len(pdf_reader.pages),
                "file_type": "pdf"
            }

            # Extract PDF info if available
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                if info.get("/Title"):
                    metadata["title"] = info.get("/Title")
                if info.get("/Author"):
                    metadata["author"] = info.get("/Author")
                if info.get("/Subject"):
                    metadata["subject"] = info.get("/Subject")

            return metadata
        except Exception as e:
            return {"file_type": "pdf", "error": str(e)}
