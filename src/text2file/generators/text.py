"""Generators for text-based file formats."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from ..generators import register_generator


@register_generator(["txt", "md", "html", "css", "js", "py", "json", "csv"])
def generate_text_file(content: str, output_path: Path) -> Path:
    """Generate a text-based file with the given content.
    
    Args:
        content: Text content to write to the file
        output_path: Path where the file should be created
        
    Returns:
        Path to the created file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    ext = output_path.suffix.lower()[1:]  # Remove the dot
    
    if ext == "json":
        # Try to parse as JSON, fall back to raw content if invalid
        try:
            json_data = json.loads(content)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            return output_path
        except json.JSONDecodeError:
            # If content is not valid JSON, save as plain text
            pass
    
    elif ext == "csv":
        # Try to parse as CSV, fall back to raw content if invalid
        try:
            # Split content into lines and then into cells
            rows = [line.split(',') for line in content.split('\n') if line.strip()]
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            return output_path
        except Exception:
            # If CSV parsing fails, save as plain text
            pass
    
    # For all other text formats, write the content as is
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path
