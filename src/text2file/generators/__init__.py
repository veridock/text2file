"""File generators and validators for different file formats."""

import importlib
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from .image_set import ImageSetGenerator
from .validators import (
    FileValidator,
    ImageFileValidator,
    PDFFileValidator,
    TextFileValidator,
    ValidationResult,
    cleanup_invalid_files,
)
from .validators import get_validator as _get_validator
from .validators import validate_file

# Type alias for generator functions
GeneratorFunc = Callable[..., Path]

# Dictionary to store registered generators
_generators: Dict[str, GeneratorFunc] = {}

# Set of supported file extensions (without leading dot)
SUPPORTED_EXTENSIONS: Set[str] = set()


def register_generator(
    extensions: List[str],
) -> Callable[[GeneratorFunc], GeneratorFunc]:
    """Decorator to register a generator function for specific file extensions.

    Args:
        extensions: List of file extensions (with or without leading dot) that this generator supports

    Returns:
        Decorator function that registers the generator
    """

    def decorator(func: GeneratorFunc) -> GeneratorFunc:
        """Register the generator function for the given extensions."""
        print(
            f"Registering generator {func.__name__} for extensions: {extensions}",
            file=sys.stderr,
        )
        for ext in extensions:
            ext_lower = ext.lower().lstrip(".")
            print(f"  - Adding extension: {ext_lower}", file=sys.stderr)
            _generators[ext_lower] = func
            SUPPORTED_EXTENSIONS.add(ext_lower)
        print(f"  Current generators: {list(_generators.keys())}", file=sys.stderr)
        return func

    return decorator


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


def register_generator(extensions: List[str]):
    """Decorator to register a generator function for specific extensions.

    Args:
        extensions: List of file extensions (without leading dot) that this
            generator handles
    """

    def decorator(func: GeneratorFunc) -> GeneratorFunc:
        for ext in extensions:
            ext_lower = ext.lower().lstrip(".")
            _generators[ext_lower] = func
            SUPPORTED_EXTENSIONS.add(ext_lower)
        return func

    return decorator


def get_generator(extension: str) -> Optional[GeneratorFunc]:
    """Get the generator function for a given file extension.

    Args:
        extension: File extension (with or without leading dot)

    Returns:
        Generator function or None if not found
    """
    ext = extension.lower().lstrip(".")
    return _generators.get(ext)


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
    ext = extension.lower().lstrip(".")
    generator = get_generator(ext)

    if generator is None:
        raise ValueError(f"No generator found for extension: {ext}")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    filepath = output_dir / filename

    # Generate the file
    print(f"Generating file: {filepath}", file=sys.stderr)
    try:
        # Call the generator function with the content and output path
        result_path = generator(content, filepath, **{})
        print(f"Successfully generated file: {result_path}", file=sys.stderr)
        return result_path
    except Exception as e:
        print(f"Error generating file: {e}", file=sys.stderr)
        raise


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
from .images import *  # noqa: F401, F403
from .office import *  # noqa: F401, F403
from .pdf import *  # noqa: F401, F403

# After all imports, print final state
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
