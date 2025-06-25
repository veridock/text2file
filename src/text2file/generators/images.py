"""Generators for image file formats."""

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from ..generators import register_generator


def get_text_dimensions(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Calculate text dimensions using getbbox method.
    
    Args:
        draw: ImageDraw instance
        text: Text to measure
        font: Font to use for measurement
        
    Returns:
        tuple: (width, height) of the text bounding box
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]  # width, height


def get_system_font():
    """Try to load a system font, falling back to default if not found."""
    # Try common system fonts
    font_names = [
        "DejaVuSans.ttf",  # Common on Linux
        "Arial.ttf",        # Common on Windows
        "Arial Unicode.ttf", # Common on macOS
        "LiberationSans-Regular.ttf",  # Common on some Linux distros
    ]
    
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, 20)
        except (IOError, OSError):
            continue
    
    # Fall back to default font
    return ImageFont.load_default()


@register_generator(["jpg", "jpeg", "png", "bmp", "gif"])
def generate_image_file(content: str, output_path: Path) -> Path:
    """Generate an image file with the given content.
    
    Args:
        content: Text content to render in the image
        output_path: Path where the image should be saved
        
    Returns:
        Path to the generated image file
    """
    # Create a blank image with white background
    width, height = 800, 600
    background_color = (255, 255, 255)  # white
    text_color = (0, 0, 0)  # black

    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Get a font
    font = get_system_font()
    
    # Calculate line height and margins
    _, text_height = get_text_dimensions(draw, "A", font)
    line_spacing = int(text_height * 0.2)  # 20% of text height as spacing
    margin = 50
    max_width = width - (2 * margin)
    
    # Wrap text to fit within the image width
    lines = []
    for line in content.split('\n'):
        # Simple word wrapping
        words = line.split()
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed the width
            test_line = ' '.join(current_line + [word])
            test_width, _ = get_text_dimensions(draw, test_line, font)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
    
    # Draw text on image
    y_position = margin
    for line in lines:
        if not line.strip():
            y_position += text_height + line_spacing
            continue
            
        text_width, text_height = get_text_dimensions(draw, line, font)
        x_position = (width - text_width) // 2  # Center the text
        
        draw.text((x_position, y_position), line, font=font, fill=text_color)
        y_position += text_height + line_spacing
        
        # Stop if we're running out of space
        if y_position > height - margin - text_height:
            break
    
    # Save the image
    image.save(output_path)
    return output_path
