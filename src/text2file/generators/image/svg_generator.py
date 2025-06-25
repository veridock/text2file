"""SVG file generator module."""

from pathlib import Path
from typing import Any, Dict, Optional

from ...utils.file_utils import create_parent_directories

# This will be set when the module is imported in __init__.py
register_generator = None


def _create_svg_content(content: str, width: int = 200, height: int = 100) -> str:
    """Create SVG content with the given text.
    
    Args:
        content: The text content to include in the SVG
        width: Width of the SVG in pixels
        height: Height of the SVG in pixels
        
    Returns:
        str: SVG content as a string
    """
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" version="1.1" 
     viewBox="0 0 {width} {height}" 
     xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="white"/>
  <text x="50%" y="50%" 
        font-family="Arial, sans-serif" 
        font-size="14" 
        text-anchor="middle" 
        dominant-baseline="middle"
        fill="black">
    {content}
  </text>
</svg>'''


def generate_svg(
    content: str,
    output_path: Path,
    width: int = 200,
    height: int = 100,
    **kwargs: Any
) -> Path:
    """Generate an SVG file with the given content.
    
    Args:
        content: The text content to include in the SVG
        output_path: Path where the SVG file should be saved
        width: Width of the SVG in pixels
        height: Height of the SVG in pixels
        **kwargs: Additional keyword arguments (ignored)
        
    Returns:
        Path: The path to the generated SVG file
    """
    svg_content = _create_svg_content(content, width, height)
    
    # Ensure parent directory exists
    ensure_directory(output_path.parent)
    
    # Write the SVG content to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return output_path


# Register the generator when this module is imported
if register_generator is not None:
    register_generator(["svg"])(generate_svg)
