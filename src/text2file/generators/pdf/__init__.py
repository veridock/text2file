"""PDF file generators."""

# Use lazy imports to avoid circular imports
import sys
from pathlib import Path
from typing import Any, Optional, Tuple, Type, TypeVar

# This will be set when the module is imported in generators/__init__.py
register_generator = None

def _get_fpdf() -> Tuple[Optional[Type], Optional[Type], Optional[Type]]:
    """Lazy import of fpdf2 to make it an optional dependency."""
    try:
        from fpdf import FPDF, XPos, YPos
        return FPDF, XPos, YPos
    except ImportError:
        return None, None, None

def generate_pdf_file(content: str, output_path: Path, **kwargs: Any) -> Path:
    """Generate a PDF file with the given content.

    Args:
        content: Text content to include in the PDF
        output_path: Path where the PDF should be saved
        **kwargs: Additional keyword arguments (ignored)

    Returns:
        Path to the generated PDF file

    Raises:
        ImportError: If fpdf2 is not installed
    """
    FPDF, XPos, YPos = _get_fpdf()
    if FPDF is None or XPos is None or YPos is None:
        raise ImportError(
            "fpdf2 is required for PDF generation. Install with: pip install fpdf2"
        )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Set margins (1 inch = 25.4 mm)
    margin = 25.4
    pdf.set_margins(margin, margin, margin)

    # Calculate available width
    available_width = pdf.w - 2 * margin

    # Split content into paragraphs
    paragraphs = content.split("\n\n")

    for para in paragraphs:
        if not para.strip():
            pdf.ln(10)  # Add space between paragraphs
            continue

        # Split into lines that fit the page width
        lines = pdf.multi_cell(
            w=available_width, h=10, txt=para, split_only=True  # line height
        )

        # Add each line to the PDF
        for line in lines:
            pdf.cell(
                w=available_width,
                h=10,  # line height
                txt=line,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

        # Add space after paragraph
        pdf.ln(5)


    # Save the PDF
    pdf.output(str(output_path))
    return output_path

def _register_generators():
    """Register all PDF generators."""
    if register_generator is not None:
        register_generator(["pdf"])(generate_pdf_file)

# This will be called after all imports are complete
def _on_import():
    if register_generator is not None:
        _register_generators()

# Register the callback to run after imports are complete
import atexit
atexit.register(_on_import)
