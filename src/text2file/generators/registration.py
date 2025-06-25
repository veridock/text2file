"""Module for registering file generators."""

import sys
from pathlib import Path
from typing import Callable, Dict, List, Set, TypeVar, cast

# Type variable for generator functions
GeneratorFunc = TypeVar('GeneratorFunc', bound=Callable[..., Path])

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
            # Remove leading dot if present
            ext = ext.lstrip('.').lower()
            _generators[ext] = func
            SUPPORTED_EXTENSIONS.add(ext)
        return func
    return decorator


def get_generator(extension: str) -> Callable[..., Path]:
    """Get the generator function for a file extension.

    Args:
        extension: File extension (with or without leading dot)

    Returns:
        Generator function if found, None otherwise
    """
    # Remove leading dot if present and convert to lowercase
    extension = extension.lstrip('.').lower()
    return _generators.get(extension)


def get_supported_extensions() -> Set[str]:
    """Get a set of all supported file extensions.
    
    Returns:
        Set of supported file extensions (without leading dots)
    """
    return SUPPORTED_EXTENSIONS.copy()
