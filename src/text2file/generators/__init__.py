"""File generators and validators for different file formats."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .registration import (
    GeneratorFunc,
    get_generator as _get_generator,
    get_supported_extensions,
    register_generator,
)
from .validators import (
    FileValidator,
    ImageFileValidator,
    PDFFileValidator,
    TextFileValidator,
    ValidationResult,
    cleanup_invalid_files,
    get_validator as _get_validator,
    validate_file,
)

# Re-export registration functions
register_generator = register_generator
get_generator = _get_generator
SUPPORTED_EXTENSIONS = get_supported_extensions()

# Re-export get_validator from validators module
get_validator = _get_validator

# Export validation functions and types
__all__ = [
    "FileValidator",
    "TextFileValidator",
    "ImageFileValidator",
    "PDFFileValidator",
    "ValidationResult",
    "cleanup_invalid_files",
    "generate_file",
    "get_generator",
    "get_validator",
    "register_generator",
    "validate_file",
    "GeneratorFunc",
    "SUPPORTED_EXTENSIONS",
]  # ImageSetGenerator will be added after import


# Module-level constant for default output directory
_DEFAULT_OUTPUT_DIR = Path.cwd()


def generate_file(
    content: str,
    extension: str,
    output_dir: Optional[Path] = None,
    prefix: str = "generated",
) -> Path:
    """Generate a file with the given content and extension.

    Args:
        content: Text content to include in the file
        extension: File extension (with or without leading dot)
        output_dir: Directory to save the file in
        prefix: Prefix for the generated filename

    Returns:
        Path to the generated file

    Raises:
        ValueError: If no generator is found for the extension
        IOError: If there's an error writing the file
    """
    # Get the generator function for the extension
    generator = get_generator(extension)
    if generator is None:
        raise ValueError(f"No generator found for extension: {extension}")

    # Use default output directory if none provided
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    else:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension.lstrip('.')}"
    output_path = output_dir / filename

    try:
        # Call the generator function
        generated_path = generator(content, output_path)
        return generated_path
    except Exception as e:
        # Clean up partially created files
        if output_path.exists():
            output_path.unlink()
        raise IOError(f"Error generating {extension} file: {str(e)}") from e


# Import and register all generators
try:
    # Import text generator first
    from .text import generate_text_file
    
    register_generator(["txt", "md", "html", "css", "js", "py", "json", "csv"])(
        generate_text_file
    )

    # Import other generators
    from .archives import *  # noqa: F401, F403
    from .office import *  # noqa: F401, F403
    from .video import *  # noqa: F401, F403
    from .image import *  # noqa: F401, F403
    
    # Lazy import of PDF generator to avoid circular imports
    from .pdf import generate_pdf_file  # noqa: F401
    register_generator(["pdf"])(generate_pdf_file)
    from .image_set import ImageSetGenerator  # noqa: F401

    # Add ImageSetGenerator to __all__
    __all__.append("ImageSetGenerator")
    
    # Process any pending registrations
    from .registration import process_pending_registrations
    process_pending_registrations()

except ImportError as e:
    print(f"Error importing generators: {e}", file=sys.stderr)  # noqa: T201
    raise
