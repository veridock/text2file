"""File generators and validators for different file formats."""

import importlib
import os
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
        for ext in extensions:
            ext_lower = ext.lower().lstrip('.')
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
    ext = extension.lower().lstrip('.')
    return _generators.get(ext)


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


# Import all generator modules to register them
# This will automatically discover and register all generators defined in this package
for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith('.py') and not module.startswith('_'):
        module_name = f"{__package__}.{module[:-3]}"
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")

# Import base generators
from .text import *  # noqa: F401, F403
from .images import *  # noqa: F401, F403
from .office import *  # noqa: F401, F403
from .archives import *  # noqa: F401, F403
