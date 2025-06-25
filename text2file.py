#!/usr/bin/env python3
"""
text2file - A utility to generate test files of various types from text content.

Usage:
    python3 text2file.py "content" [extensions...]

Example:
    python3 text2file.py "Example content" pdf md jpg
"""

import argparse
import sys
import textwrap
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

def generate_text_file(content: str, extension: str) -> str:
    """Generate a text-based file with the given content."""
    filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def generate_pdf(content: str) -> str:
    """Generate a PDF file with the given content."""
    try:
        from fpdf import FPDF, XPos, YPos

        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)  # Using standard PDF font

        # Split content into lines that fit the page
        lines = textwrap.wrap(content, width=80)
        for line in lines:
            pdf.cell(200, 10, text=line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.output(filename)
        return filename
    except ImportError:
        print("Error: fpdf module not found. Install with: pip install fpdf2")
        return None

def get_text_dimensions(draw, text, font):
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

def generate_image(content: str, extension: str) -> str:
    """Generate an image file with the given content.
    
    Args:
        content: Text content to render in the image
        extension: Image file extension (jpg, png, etc.)
        
    Returns:
        str: Path to the generated image file or None if failed
    """
    try:
        # Create a blank image with white background
        width, height = 800, 600
        background_color = (255, 255, 255)  # white
        text_color = (0, 0, 0)  # black

        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Try to use a default font
        font = None
        for font_name in ["DejaVuSans.ttf", "Arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 20)
                break
            except (IOError, OSError):
                continue
        
        if font is None:
            font = ImageFont.load_default()

        # Wrap text
        lines = textwrap.wrap(content, width=40)
        y_text = 50
        line_spacing = 5
        margin = 50

        for line in lines:
            # Get text size and position it in the center
            text_width, text_height = get_text_dimensions(draw, line, font)
            x = (width - text_width) / 2
            draw.text((x, y_text), line, font=font, fill=text_color)
            y_text += text_height + line_spacing

            # Stop if we're running out of space
            if y_text > height - margin:
                break

        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        image.save(filename)
        return filename
    except ImportError:
        print("Error: Pillow module not found. Please install it with: pip install pillow")
        return None

def main():
    """Main function to handle command line arguments and file generation."""
    parser = argparse.ArgumentParser(
        description='Generate test files with the given content.'
    )
    parser.add_argument(
        'content',
        type=str,
        help='Content to include in the generated files'
    )
    parser.add_argument(
        'extensions',
        nargs='+',
        help='File extensions to generate (e.g., pdf md jpg)'
    )

    args = parser.parse_args()

    if not args.extensions:
        print("Error: At least one file extension must be provided.")
        sys.exit(1)

    generated_files = []
    text_extensions = ['txt', 'md', 'csv', 'json', 'html', 'css', 'js', 'py']
    image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'gif']

    for ext in args.extensions:
        ext_lower = ext.lower().lstrip('.')
        filename = None

        try:
            if ext_lower in text_extensions:
                filename = generate_text_file(args.content, ext_lower)
            elif ext_lower == 'pdf':
                filename = generate_pdf(args.content)
            elif ext_lower in image_extensions:
                filename = generate_image(args.content, ext_lower)
            else:
                print(f"Unsupported file extension: {ext_lower}")
                continue

            if filename:
                generated_files.append(filename)
                print(f"Generated: {filename}")

        except Exception as e:
            print(f"Error generating {ext_lower} file: {e}")

    if generated_files:
        print("\nSuccessfully generated files:")
        print("- " + "\n- ".join(generated_files))
    else:
        print("No files were generated.")

if __name__ == "__main__":
    main()
