"""PDF processing module for converting PDFs to structured markdown.

This module handles PDF to markdown conversion using Docling DocumentConverter.
It preserves document structure including headings, lists, tables, and page information.
"""

from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter, ConversionResult, ConversionStatus
from docling_core.types.doc import DoclingDocument

from src.config import config


class PDFConversionError(Exception):
    """Raised when PDF conversion fails."""

    pass


def convert_pdf(pdf_path: Path) -> DoclingDocument:
    """Convert a PDF file to a DoclingDocument.

    Args:
        pdf_path: Path to the PDF file to convert.

    Returns:
        DoclingDocument object containing the structured document content.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        PDFConversionError: If the conversion fails.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    try:
        converter = DocumentConverter()
        result: ConversionResult = converter.convert(str(pdf_path))

        if result.status != ConversionStatus.SUCCESS:
            raise PDFConversionError(f"PDF conversion failed with status: {result.status}")

        return result.document

    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError, PDFConversionError)):
            raise
        raise PDFConversionError(f"Failed to convert PDF: {e}") from e


def convert_pdf_to_markdown(pdf_path: Path) -> str:
    """Convert a PDF file to markdown format.

    Args:
        pdf_path: Path to the PDF file to convert.

    Returns:
        Markdown string representation of the document.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        PDFConversionError: If the conversion fails.
    """
    document = convert_pdf(pdf_path)
    return document.export_to_markdown()


def process_pdf_with_details(pdf_path: Path) -> tuple[DoclingDocument, str]:
    """Convert a PDF and return both the document object and markdown.

    This function is useful when you need both the structured document
    (for chunking) and the markdown representation (for preview/storage).

    Args:
        pdf_path: Path to the PDF file to convert.

    Returns:
        Tuple of (DoclingDocument, markdown_string).

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        PDFConversionError: If the conversion fails.
    """
    document = convert_pdf(pdf_path)
    markdown = document.export_to_markdown()
    return document, markdown
