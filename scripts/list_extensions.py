#!/usr/bin/env python3
"""List all supported file extensions."""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.text2file.generators import SUPPORTED_EXTENSIONS  # noqa: E402


def main():
    """Print all supported file extensions, one per line."""
    # Call the SUPPORTED_EXTENSIONS function to get the set of extensions
    extensions = SUPPORTED_EXTENSIONS()
    for ext in sorted(extensions):
        print(ext)


if __name__ == "__main__":
    main()
