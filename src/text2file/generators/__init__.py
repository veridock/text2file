"""File generators and validators for different file formats."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypeVar, cast

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
    "ImageSetGenerator",
]


def generate_file(
    content: str,
    extension: str,
    output_dir: Path = Path.cwd(),
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
        raise IOError(f"Error generating {extension} file: {str(e)}")


# Explicitly import and register the text generator first
try:
    print("Importing text generator...", file=sys.stderr)
    from .text import generate_text_file

    # Manually register the text generator with all its extensions
    register_generator(["txt", "md", "html", "css", "js", "py", "json", "csv"])(
        generate_text_file
    )
    print("Successfully registered text generator", file=sys.stderr)
    print(
        f"Registered extensions after text: {sorted(SUPPORTED_EXTENSIONS)}",
        file=sys.stderr,
    )
except ImportError as e:
    print(f"Failed to import text generator: {e}", file=sys.stderr)
    raise


def get_generator(extension: str) -> Optional[GeneratorFunc]:
    """Get the generator function for a file extension.

    Args:
        extension: File extension (with or without leading dot)

    Returns:
        Generator function if found, None otherwise
    """
    ext = extension.lower().lstrip(".")
    print(f"Looking up generator for extension: {ext!r}", file=sys.stderr)
    print(f"Available extensions: {sorted(SUPPORTED_EXTENSIONS)}", file=sys.stderr)
    generator = _generators.get(ext)
    print(f"Found generator: {generator is not None}", file=sys.stderr)
    return generator


# Import other generators after defining the registration system
print("Importing other generators...", file=sys.stderr)
from .archives import *  # noqa: F401, F403
from .image import *  # noqa: F401, F403
from .image_set import *  # noqa: F401, F403
from .office import *  # noqa: F401, F403
from .pdf import *  # noqa: F401, F403
from .text import *  # noqa: F401, F403
from .video import *  # noqa: F401, F403
print(f"Final registered generators: {list(_generators.keys())}", file=sys.stderr)
print(f"Final supported extensions: {sorted(SUPPORTED_EXTENSIONS)}", file=sys.stderr)

# Then import remaining modules
for module in os.listdir(os.path.dirname(__file__)):
    if (
        module.endswith(".py")
        and not module.startswith("_")
        and module
        not in [
            "text.py",
            "images.py",
            "office.py",
            "archives.py",
            "pdf.py",
            "base.py",
            "validators.py",
        ]
    ):
        module_name = f"{__package__}.{module[:-3]}"
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)
