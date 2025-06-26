"""Excel file generator module."""

import io
import logging
from pathlib import Path
from typing import Optional, Union

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

logger = logging.getLogger(__name__)

def _parse_csv_content(content: str) -> list[list[str]]:
    """Parse CSV-like content into a 2D list of strings.
    
    Args:
        content: CSV content as a string
        
    Returns:
        List of rows, where each row is a list of cell values
    """
    return [line.split(',') for line in content.strip().split('\n')]

def _auto_adjust_columns(worksheet: Worksheet) -> None:
    """Auto-adjust column widths based on content.
    
    Args:
        worksheet: The worksheet to adjust
    """
    for column_cells in worksheet.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        worksheet.column_dimensions[column].width = min(adjusted_width, 50)

def generate_excel_file(
    content: str,
    output_path: Union[str, Path],
    sheet_name: str = "Sheet1",
    auto_adjust: bool = True
) -> Path:
    """Generate an Excel file from the given content.
    
    Args:
        content: The content to convert to Excel. Should be in CSV format.
        output_path: Path where the Excel file will be saved.
        sheet_name: Name of the worksheet.
        auto_adjust: Whether to auto-adjust column widths.
        
    Returns:
        Path to the generated Excel file.
    """
    output_path = Path(output_path)
    
    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    
    # Parse the CSV content
    rows = _parse_csv_content(content)
    
    # Add data to worksheet
    for row_idx, row in enumerate(rows, 1):
        for col_idx, value in enumerate(row, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value.strip())
    
    # Auto-adjust column widths if requested
    if auto_adjust and rows:
        _auto_adjust_columns(ws)
    
    # Save the workbook
    wb.save(str(output_path))
    logger.debug(f"Generated Excel file: {output_path}")
    
    return output_path

# Register this generator
def register() -> None:
    """Register the Excel file generator."""
    from .registration import register_generator
    
    @register_generator(["xlsx", "xls"])
    def excel_generator(
        content: str,
        output_path: Union[str, Path],
        **kwargs
    ) -> Path:
        """Generate an Excel file from the given content.
        
        Args:
            content: The content to convert to Excel.
            output_path: Path where the Excel file will be saved.
            **kwargs: Additional keyword arguments for generate_excel_file.
            
        Returns:
            Path to the generated Excel file.
        """
        return generate_excel_file(content, output_path, **kwargs)
