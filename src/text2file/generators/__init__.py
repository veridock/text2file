"""File generators and validators for different file formats."""

import importlib
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from .image_set import ImageSetGenerator
from .validators import (
    FileValidator,
    TextFileValidator,
    ImageFileValidator,
    PDFFileValidator,
    ValidationResult,
    cleanup_invalid_files,
    get_validator as _get_validator,
    validate_file,
)

# Type variable for generator functions
GeneratorFunc = Callable[[str, Path, str], Path]

# Dictionary to store generator functions by extension
_generators: Dict[str, GeneratorFunc] = {}

# Set of supported extensions
SUPPORTED_EXTENSIONS: Set[str] = set()

# Re-export get_validator from validators module
get_validator = _get_validator

# Export validation functions and types
__all__ = [
    'FileValidator',
    'TextFileValidator',
    'ImageFileValidator',
    'PDFFileValidator',
    'ValidationResult',
    'cleanup_invalid_files',
    'generate_file',
    'get_generator',
    'get_validator',
    'register_generator',
    'validate_file',
    'GeneratorFunc',
    'SUPPORTED_EXTENSIONS',
    'ImageSetGenerator',
]


def register_generator(
    extensions: List[str]
) -> Callable[[GeneratorFunc], GeneratorFunc]:
    """Decorator to register a generator function for specific extensions.
    
    Args:
        extensions: List of file extensions (without leading dot) that this
            generator handles
    """
    def decorator(func: GeneratorFunc) -> GeneratorFunc:
        print(f"Registering generator {func.__name__} for extensions: {extensions}", file=sys.stderr)
        for ext in extensions:
            ext_lower = ext.lower().lstrip('.')
            print(f"  - Adding extension: {ext_lower}", file=sys.stderr)
            _generators[ext_lower] = func
            SUPPORTED_EXTENSIONS.add(ext_lower)
        print(f"  Current generators: {_generators.keys()}", file=sys.stderr)
        return func
    return decorator


def get_generator(extension: str) -> Optional[GeneratorFunc]:
    """Get the generator function for a given file extension.
    
    Args:
        extension: File extension (with or without leading dot)
        
    Returns:
        Generator function or None if not found
    """
    ext = extension.lower().lstrip('.')
    print(f"Looking up generator for extension: {ext!r}", file=sys.stderr)  # Debug
    print(f"Available extensions: {sorted(_generators.keys())}", file=sys.stderr)  # Debug
    generator = _generators.get(ext)
    print(f"Found generator: {generator is not None}", file=sys.stderr)  # Debug
    return generator


def generate_file(
    content: str,
    extension: str,
    output_dir: Path = Path.cwd(),
    prefix: str = "generated"
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
    ext = extension.lower().lstrip('.')
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
    return generator(content, filepath)


print("Importing generator modules...", file=sys.stderr)

# Import all generator modules to register them
# Import base generators first
print("Importing text generator...", file=sys.stderr)
try:
    from .text import *  # noqa: F401, F403
    print("Successfully imported text generator", file=sys.stderr)
except ImportError as e:
    print(f"Failed to import text generator: {e}", file=sys.stderr)

print("Importing other generators...", file=sys.stderr)
from .images import *  # noqa: F401, F403
from .office import *  # noqa: F401, F403
from .archives import *  # noqa: F401, F403
from .pdf import *  # noqa: F401, F403

# Then import remaining modules
for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith('.py') and not module.startswith('_') and module not in [
        'text.py', 'images.py', 'office.py', 'archives.py', 'pdf.py', 'base.py', 'validators.py'
    ]:
        module_name = f"{__package__}.{module[:-3]}"
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)
