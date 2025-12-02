from pathlib import Path

from docling.document_converter import DocumentConverter, ConversionResult, ConversionStatus
from docling_core.types.doc import DoclingDocument

from src.config import config


class PDFConversionError(Exception):
    pass


def convert_pdf(pdf_path: Path) -> DoclingDocument:
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
    document = convert_pdf(pdf_path)
    return document.export_to_markdown()


def process_pdf_with_details(pdf_path: Path) -> tuple[DoclingDocument, str]:
    document = convert_pdf(pdf_path)
    markdown = document.export_to_markdown()
    return document, markdown
