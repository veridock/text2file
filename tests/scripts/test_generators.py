#!/usr/bin/env python3
"""Script to test all file generators and validators."""

import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Type

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.text2file.generators import get_generator, SUPPORTED_EXTENSIONS
from src.text2file.validators import get_validator


def get_test_content(extension: str) -> str:
    """Get appropriate test content based on file type."""
    content_map = {
        'py': 'print("Hello, World!")\nprint("This is a test Python script.")',
        'sh': '#!/bin/bash\necho "Hello, World!"\necho "This is a test shell script."',
        'md': '# Test Document\n\nThis is a **test** markdown file.\n\n- Item 1\n- Item 2\n\n```python\nprint("Code block")\n```',
        'txt': 'This is a test text file.\nIt has multiple lines.\nAnd some special characters: !@#$%^&*()',
        'json': '{\n  "name": "test",\n  "value": 42,\n  "items": [1, 2, 3],\n  "nested": {\n    "key": "value"\n  }\n}',
        'yaml': '---\nname: test\nvalue: 42\nitems:\n  - 1\n  - 2\n  - 3\nnested:\n  key: value',
        'html': '<!DOCTYPE html>\n<html>\n<head>\n  <title>Test</title>\n</head>\n<body>\n  <h1>Hello, World!</h1>\n  <p>This is a test HTML file.</p>\n</body>\n</html>',
        'css': 'body {\n  font-family: Arial, sans-serif;\n  margin: 0;\n  padding: 20px;\n  background-color: #f0f0f0;\n}\n\nh1 {\n  color: #333;\n}',
        'js': '// Test JavaScript file\nfunction hello(name) {\n  console.log(`Hello, ${name}!`);\n}\n\nhello("World");',
        'jpg': 'This is a test image. The actual image data would be binary.',
    }
    
    # Get base extension (without dot)
    base_ext = extension.lstrip('.').lower()
    return content_map.get(base_ext, f'Test content for .{base_ext} file.')


def test_generator(extension: str, output_dir: Path) -> Tuple[bool, str, Optional[Path]]:
    """Test a single generator and validator."""
    try:
        # Get the generator and validator
        generator = get_generator(extension)
        validator = get_validator(f'test.{extension}')
        
        if generator is None:
            return False, f"No generator found for extension: {extension}", None
            
        if validator is None:
            return False, f"No validator found for extension: {extension}", None
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate test file
        test_content = get_test_content(extension)
        output_path = output_dir / f'test_{len(list(output_dir.glob("*")))}.{extension}'
        
        # Generate the file
        try:
            generated_path = generator(test_content, output_path)
        except Exception as e:
            return False, f"Error generating .{extension} file: {str(e)}", None
        
        # Validate the generated file
        try:
            result = validator.validate(str(generated_path))
            if not result.is_valid:
                return False, f"Validation failed for .{extension}: {result.message}", generated_path
        except Exception as e:
            return False, f"Error validating .{extension} file: {str(e)}", generated_path
        
        return True, f"Successfully generated and validated .{extension} file", generated_path
        
    except Exception as e:
        return False, f"Unexpected error testing .{extension}: {str(e)}", None


def main():
    """Main function to test all generators and validators."""
    # Create output directory
    output_dir = project_root / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    print(f"Testing all generators and validators. Output will be saved to: {output_dir}")
    print("-" * 80)
    
    # Test each supported extension
    results = []
    for ext in sorted(SUPPORTED_EXTENSIONS):
        success, message, file_path = test_generator(ext, output_dir)
        status = "✅" if success else "❌"
        print(f"{status} {ext:6} - {message}")
        results.append((ext, success, message, file_path))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"\n✅ {success_count}/{total} generators passed")
    
    # Print failures
    failures = [(ext, msg) for ext, success, msg, _ in results if not success]
    if failures:
        print("\n❌ Failures:")
        for ext, msg in failures:
            print(f"  - {ext}: {msg}")
    
    # Print generated files
    print("\nGenerated files:")
    for ext, success, _, file_path in results:
        if success and file_path and file_path.exists():
            print(f"  - {file_path.relative_to(project_root)}")
    
    return 0 if success_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
