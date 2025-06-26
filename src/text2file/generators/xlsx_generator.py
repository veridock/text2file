"""Generator for Excel (.xlsx) files."""

from pathlib import Path
from typing import Any, Dict, Optional

import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from .base import FileGeneratorBase


class XLSXGenerator(FileGeneratorBase):
    """Generator for Excel (.xlsx) files."""

    EXTENSIONS = {"xlsx"}
    
    def __init__(self):
        """Initialize the XLSX generator."""
        super().__init__()
        self._workbook: Optional[Workbook] = None
        self._worksheet: Optional[Worksheet] = None
    
    def _parse_csv_content(self, content: str) -> list[list[str]]:
        """Parse CSV-like content into rows and cells."""
        return [line.split(",") for line in content.strip().split("\n")]
    
    def _auto_adjust_columns(self, worksheet: Worksheet) -> None:
        """Auto-adjust column widths based on content."""
        for column_cells in worksheet.columns:
            if not column_cells:  # Skip empty columns
                continue
                
            max_length = 0
            column = column_cells[0].column_letter  # Get the column name
            
            for cell in column_cells:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:  # noqa: BLE001
                    continue
                    
            if max_length > 0:
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column].width = adjusted_width
    
    def generate(
        self,
        content: str,
        output_path: Path,
        **options: Dict[str, Any],
    ) -> Path:
        """
        Generate an Excel file from the given content.

        Args:
            content: The content to write to the file. For XLSX, this should be
                    a CSV-like string where rows are separated by newlines and
                    cells by commas.
            output_path: The path where the file should be saved.
            **options: Additional options for file generation.
                - sheet_name: Name of the worksheet (default: 'Sheet1')
                - auto_adjust: Whether to auto-adjust column widths (default: True)
        """
        # Create a new workbook and select the active worksheet
        self._workbook = openpyxl.Workbook()
        sheet_name = options.get("sheet_name", "Sheet1")
        self._worksheet = self._workbook.active
        self._worksheet.title = sheet_name
        
        # Parse the CSV-like content
        rows = self._parse_csv_content(content)
        
        # Write data to the worksheet
        for row_idx, row in enumerate(rows, 1):
            for col_idx, value in enumerate(row, 1):
                self._worksheet.cell(row=row_idx, column=col_idx, value=value.strip())
        
        # Auto-adjust column widths if requested
        if options.get("auto_adjust", True):
            self._auto_adjust_columns(self._worksheet)
        
        # Save the workbook
        try:
            self._workbook.save(output_path)
            return output_path
        except Exception as e:
            raise IOError(f"Failed to save XLSX file: {e}") from e
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up any resources used by the generator."""
        if self._workbook:
            try:
                self._workbook.close()
            except Exception:  # noqa: BLE001
                pass  # Ignore errors during cleanup
            self._workbook = None
        self._worksheet = None


def register(registry):
    """Register the XLSX generator."""
    registry.register(XLSXGenerator())
