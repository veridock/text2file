# Text2File

[![PyPI version](https://badge.fury.io/py/text2file.svg)](https://badge.fury.io/py/text2file)
[![Python Version](https://img.shields.io/pypi/pyversions/text2file.svg)](https://pypi.org/project/text2file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/veridock/text2file/actions/workflows/tests.yml/badge.svg)](https://github.com/veridock/text2file/actions)
[![Codecov](https://codecov.io/gh/veridock/text2file/branch/main/graph/badge.svg)](https://codecov.io/gh/veridock/text2file)

A powerful utility to generate test files in various formats from text content. Perfect for testing, development, and automation tasks.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Using pip (recommended)](#using-pip-recommended)
  - [From source](#from-source)
- [Usage](#usage)
  - [Basic Syntax](#basic-syntax)
  - [Available Commands](#available-commands)
  - [Examples](#examples)
- [File Format Examples](#file-format-examples)
  - [Text Files](#text-files)
  - [Code Files](#code-files)
  - [Documents](#documents)
  - [Spreadsheets](#spreadsheets)
  - [Images](#images)
  - [Archives](#archives)
- [API Reference](#api-reference)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🚀 Generate files in multiple formats with a single command
- 📄 Support for various file types:
  - **Text**: `.txt`, `.md`, `.html`, `.css`, `.js`, `.py`, `.json`, `.csv`
  - **Documents**: `.pdf`, `.docx`, `.odt`
  - **Spreadsheets**: `.xlsx`
  - **Images**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`
  - **Archives**: `.zip`, `.tar`, `.tar.gz`, `.tgz`
- ✅ File validation to ensure generated files are not corrupted
- 🔄 Clean up invalid files with a single command
- 📂 Customizable output directory and filename prefix
- 🔍 Recursive directory scanning for validation and cleanup
- 🛠️ Extensible architecture for adding new file formats
- 🧪 Built-in testing and validation

## Installation

### Using pip (recommended)

```bash
pip install text2file
```

### From source

1. Clone the repository:
   ```bash
   git clone https://github.com/veridock/text2file.git
   cd text2file
   ```

2. Install with Poetry (recommended):
   ```bash
   poetry install
   ```

   Or with pip:
   ```bash
   pip install .
   ```

## Usage

### Basic Syntax

```bash
text2file [COMMAND] [OPTIONS]
```

### Available Commands

- `generate` - Generate files in various formats
- `generate-set` - Generate a set of images from a JSON configuration
- `validate` - Validate generated files
- `cleanup` - Clean up invalid files
- `--version` - Show version and exit
- `--help` - Show help message and exit

### Examples

#### Generate a text file
```bash
text2file generate --content "Hello, World!" --extension txt
```

#### Generate a set of images from a JSON configuration

Create a JSON file (e.g., `icons.json`) with the following format:

```json
{
  "icons": [
    {"src": "icon-16x16.png", "sizes": "16x16"},
    {"src": "icon-32x32.png", "sizes": "32x32"},
    {"src": "icon-64x64.png", "sizes": "64x64"}
  ]
}
```

Then run:

```bash
# Generate placeholder images with default text
text2file generate-set icons.json

# Use a base image and resize it
text2file generate-set icons.json --base-image source-icon.png

# Customize the placeholder appearance
text2file generate-set icons.json --text "My App" --background-color "#f0f0f0" --text-color "#333333"
```

Options:
- `-o, --output-dir`: Output directory (default: current directory)
- `-b, --base-image`: Base image to use for resizing (optional)
- `--bg, --background-color`: Background color for placeholders (default: "#ffffff")
- `-t, --text`: Text to render on placeholder images
- `--fg, --text-color`: Text color for placeholders (default: "#000000")

#### Generate multiple files with different formats
```bash
text2file generate --content "Sample content" --extension txt,md,html --output-dir ./output
```

#### Validate generated files
```bash
text2file validate --path ./output --recursive --verbose
```

#### Clean up invalid files
```bash
text2file cleanup --path ./output --recursive --dry-run
```

## File Format Examples

### Text Files

#### Plain Text (.txt)
```bash
text2file generate --content "This is a plain text file" --extension txt
```

#### Markdown (.md)
```bash
content="# Sample Markdown\n\n- Item 1\n- Item 2\n- Item 3"
text2file generate --content "$content" --extension md
```

### Code Files

#### Python (.py)
```bash
content="def hello_world():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    hello_world()"
text2file generate --content "$content" --extension py
```

#### JavaScript (.js)
```bash
content="function helloWorld() {\n  console.log('Hello, World!');\n}\n\nhelloWorld();"
text2file generate --content "$content" --extension js
```

### Documents

#### PDF (.pdf)
```bash
text2file generate --content "This is a sample PDF document" --extension pdf
```

#### Word Document (.docx)
```bash
text2file generate --content "This is a sample Word document" --extension docx
```

### Spreadsheets

#### Excel (.xlsx)
```bash
content="Name,Age,City\nJohn,30,New York\nAlice,25,London"
text2file generate --content "$content" --extension xlsx
```

### Image Sets

Generate multiple images from a JSON configuration file. This is useful for creating icon sets or multiple resolutions of the same image.

#### JSON Configuration Format

Create a file (e.g., `icons.json`) with the following structure:

```json
{
  "icons": [
    {
      "src": "icon-16x16.png",
      "sizes": "16x16"
    },
    {
      "src": "icon-32x32.png",
      "sizes": "32x32"
    },
    {
      "src": "subdir/icon-64x64.png",
      "sizes": "64x64"
    }
  ]
}
```

Each entry in the `icons` array should have:
- `src`: Output file path (relative to output directory)
- `sizes`: Dimensions in format "WIDTHxHEIGHT" (e.g., "32x32")

#### Usage Examples

```bash
# Generate placeholder images with default text
text2file generate-set icons.json

# Use a base image and resize it
text2file generate-set icons.json --base-image source-icon.png

# Customize the placeholder appearance
text2file generate-set icons.json --text "My App" --background-color "#f0f0f0" --text-color "#333333"

# Specify output directory
text2file generate-set icons.json --output-dir ./output
```

#### Options
- `-o, --output-dir`: Output directory (default: current directory)
- `-b, --base-image`: Base image to use for resizing (optional)
- `--bg, --background-color`: Background color for placeholders (default: "#ffffff")
- `-t, --text`: Text to render on placeholder images
- `--fg, --text-color`: Text color for placeholders (default: "#000000")

### Single Images

#### JPEG (.jpg, .jpeg)
```bash
text2file generate --content "Sample image content" --extension jpg --width 800 --height 600
```

#### PNG (.png)
```bash
text2file generate --content "Sample image content" --extension png --width 800 --height 600
```

### Archives

#### ZIP (.zip)
```bash
text2file generate --content "Sample content for archive" --extension zip
```

#### TAR.GZ (.tar.gz)
```bash
text2file generate --content "Sample content for tar.gz archive" --extension tar.gz
```

## API Reference

### text2file.generate_file(content: str, extension: str, output_dir: str = ".", filename: Optional[str] = None) -> str
Generate a file with the given content and extension.

#### Parameters
- `content`: The content to write to the file
- `extension`: The file extension (without dot)
- `output_dir`: Output directory (default: current directory)
- `filename`: Optional custom filename (without extension)

#### Returns
- Path to the generated file

### text2file.validate_file(filepath: str) -> bool
Validate if a file is not corrupted.

#### Parameters
- `filepath`: Path to the file to validate

#### Returns
- `True` if file is valid, `False` otherwise

### text2file.cleanup_invalid_files(directory: str, recursive: bool = False, dry_run: bool = False) -> List[str]
Remove invalid files from a directory.

#### Parameters
- `directory`: Directory to clean up
- `recursive`: Whether to scan subdirectories
- `dry_run`: If True, only show what would be deleted

#### Returns
- List of removed files

## Development

### Prerequisites
- Python 3.8+
- [Poetry](https://python-poetry.org/)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/veridock/text2file.git
   cd text2file
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Run linter
ruff check .

# Format code
black .

# Check types
mypy .
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Commands

#### Generate Files

```bash
text2file generate "Your text content" [EXTENSIONS...] [OPTIONS]
```

**Options:**
- `-o, --output-dir PATH`: Output directory (default: current directory)
- `-p, --prefix TEXT`: Filename prefix (default: "generated")
- `--help`: Show help message and exit

**Examples:**

1. Generate a simple text file:
   ```bash
   text2file generate "This is a test file" txt
   ```

2. Generate multiple file formats at once:
   ```bash
   text2file generate "Sample content" txt md pdf jpg
   ```

3. Custom output directory and prefix:
   ```bash
   text2file generate "Test content" -o ./output -p custom_ txt pdf
   ```

#### Validate Files

```bash
text2file validate PATH [OPTIONS]
```

**Options:**
- `-r, --recursive`: Recursively validate files in subdirectories
- `-v, --verbose`: Show detailed validation results
- `--json`: Output results in JSON format
- `--help`: Show help message and exit

**Examples:**

1. Validate a single file:
   ```bash
   text2file validate document.pdf
   ```

2. Validate all files in a directory recursively:
   ```bash
   text2file validate ./test_files -r
   ```

3. Get detailed validation output in JSON:
   ```bash
   text2file validate ./test_files --json
   ```

#### Clean Up Invalid Files

```bash
text2file cleanup PATH [OPTIONS]
```

**Options:**
- `-r, --recursive`: Recursively clean up files in subdirectories
- `--dry-run`: Show what would be deleted without actually deleting
- `-v, --verbose`: Show detailed information
- `--help`: Show help message and exit

**Examples:**

1. Clean up invalid files in a directory:
   ```bash
   text2file cleanup ./test_files
   ```

2. Preview what would be deleted (dry run):
   ```bash
   text2file cleanup ./test_files --dry-run -v
   ```

## File Format Examples

### Text Files (`.txt`, `.md`)
```bash
text2file generate "# Markdown Title\n\nThis is a **markdown** file with *formatting*.\n\n- Item 1\n- Item 2\n- Item 3" md
```

### Code Files (`.py`, `.js`, `.html`)
```bash
text2file generate "def hello_world():\n    print('Hello, World!')" py
```

### Images (`.jpg`, `.png`)
```bash
text2file generate "Sample text to be converted to image" jpg png
```

### Documents (`.pdf`, `.docx`)
```bash
text2file generate "Formal Document\n\nThis is a sample document with multiple paragraphs. The text will be automatically wrapped to fit the output format. Great for creating test data!" pdf docx
```

## Development

### Setup

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Run tests:
   ```bash
   poetry run pytest
   ```

3. Run linter:
   ```bash
   poetry run ruff check .
   ```

4. Run formatter:
   ```bash
   poetry run black .
   ```

### Adding New File Formats

1. Create a new generator function in `src/text2file/generators/`
2. Add validation logic in `src/text2file/validators.py` if needed
3. Register the generator in `src/text2file/__init__.py`
4. Add tests in `tests/`
5. Update documentation

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.
