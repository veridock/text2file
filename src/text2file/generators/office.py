"""Generators for office document formats."""

import io
from pathlib import Path
from typing import Optional

from ..generators import register_generator


def _get_docx():
    """Lazy import of python-docx to make it an optional dependency."""
    try:
        from docx import Document

        return Document
    except ImportError:
        return None


def _get_openpyxl():
    """Lazy import of openpyxl to make it an optional dependency."""
    try:
        from openpyxl import Workbook

        return Workbook
    except ImportError:
        return None


@register_generator(["docx"])
def generate_docx_file(content: str, output_path: Path) -> Optional[Path]:
    """Generate a DOCX file with the given content.

    Args:
        content: Text content to include in the document
        output_path: Path where the document should be saved

    Returns:
        Path to the generated document or None if failed
    """
    Document = _get_docx()
    if Document is None:
        raise ImportError(
            "python-docx is required for DOCX generation. Install with: pip install python-docx"
        )

    doc = Document()
    doc.add_paragraph(content)
    doc.save(str(output_path))
    return output_path


@register_generator(["xlsx"])
def generate_xlsx_file(content: str, output_path: Path) -> Optional[Path]:
    """Generate an XLSX file with the given content.

    Args:
        content: Text content to include in the spreadsheet
        output_path: Path where the spreadsheet should be saved

    Returns:
        Path to the generated spreadsheet or None if failed
    """
    Workbook = _get_openpyxl()
    if Workbook is None:
        raise ImportError(
            "openpyxl is required for XLSX generation. Install with: pip install openpyxl"
        )

    wb = Workbook()
    ws = wb.active

    # Split content into rows and cells
    rows = [line.split("\t") for line in content.split("\n") if line.strip()]

    for row_idx, row in enumerate(rows, 1):
        for col_idx, cell_value in enumerate(row, 1):
            ws.cell(row=row_idx, column=col_idx, value=cell_value)

    wb.save(str(output_path))
    return output_path


@register_generator(["odt"])
def generate_odt_file(content: str, output_path: Path) -> Optional[Path]:
    """Generate an ODT file with the given content.

    Args:
        content: Text content to include in the document
        output_path: Path where the document should be saved

    Returns:
        Path to the generated document or None if failed
    """
    try:
        from odf import opendocument, style, text
    except ImportError:
        raise ImportError(
            "python-odf is required for ODT generation. Install with: pip install python-odf"
        )

    # Create a new ODF text document
    doc = opendocument.OpenDocumentText()

    # Add styles
    s = doc.styles

    # Add automatic styles
    para_style = style.Style(name="Standard", family="paragraph")
    para_style.addElement(style.TextProperties(fontfamily="Arial", fontsize="12pt"))
    doc.automaticstyles.addElement(para_style)

    # Add content
    for line in content.split("\n"):
        p = text.P(stylename=para_style, text=line)
        doc.text.addElement(p)

    # Save the document
    doc.save(str(output_path), True)
    return output_path
