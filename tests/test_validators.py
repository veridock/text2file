#!/usr/bin/env python3
"""Test script for file validators."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from text2file.validators import get_validator


def test_validator(file_path: str):
    """Test the appropriate validator for a given file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return

    # Get the appropriate validator for the file
    validator_class = get_validator(file_path)
    if validator_class is None:
        print(f"No validator found for file: {file_path}")
        return

    print(f"\nTesting validator for: {file_path}")
    print(f"Validator: {validator_class.__name__}")

    # Create an instance of the validator
    validator = validator_class()

    # Test validation
    result = validator.validate(file_path)
    print(f"Validation result: {result.is_valid}")
    if not result.is_valid:
        print(f"  Error: {result.error}")

    # Test file type detection if the method exists
    if hasattr(validator, "detect_file_type"):
        print(f"File type: {validator.detect_file_type(file_path)}")

    # Test MIME type detection if the method exists
    if hasattr(validator, "detect_mime_type"):
        print(f"MIME type: {validator.detect_mime_type(file_path)}")

    # Test file extension if the attribute exists
    if hasattr(validator, "extension"):
        print(f"Expected extension: {validator.extension}")
    else:
        print("No extension attribute found for this validator")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_validators.py <file1> [file2 ...]")
        print("Testing with sample files...")
        # Test with the sample file we created
        test_validator("samples/test.txt")
    else:
        for file_path in sys.argv[1:]:
            test_validator(file_path)
