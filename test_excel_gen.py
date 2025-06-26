#!/usr/bin/env python3
"""Test script for Excel file generation."""

import sys
from pathlib import Path
from text2file.generators.excel import ExcelGenerator


def main():
    # Test data in CSV format
    content = """Name,Age,City
John,30,New York
Alice,25,London
Bob,35,Paris"""

    # Output file path - save in current directory
    output_path = Path("test_excel.xlsx")

    try:
        # Generate the Excel file
        result_path = ExcelGenerator.generate(
            content=content,
            output_path=output_path,
            sheet_name="Employees",
            auto_adjust=True,
        )
        print(f"✓ Successfully generated Excel file: {result_path}")
        print(f"   File size: {result_path.stat().st_size} bytes")
        return 0
    except Exception as e:
        print(f"✗ Error generating Excel file: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
