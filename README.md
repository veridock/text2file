# text2file

A powerful utility for generating test files in various formats from text content. Perfect for testing file processing pipelines, creating sample data, or generating documentation assets.

## Features

- Generate files in multiple formats from a single command
- Supports various output formats:
  - Text files (`.txt`, `.md`, `.html`, etc.)
  - PDF documents (`.pdf`)
  - Image files (`.jpg`, `.png`, `.bmp`, `.gif`)
- Customizable output with text wrapping and formatting
- Unique filenames with timestamps to prevent collisions
- Easy to extend with new file format handlers

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/text2file.git
   cd text2file
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic syntax:
```bash
python3 text2file.py "Your text content here" [extensions...]
```

### Examples

1. Generate a simple text file:
   ```bash
   python3 text2file.py "This is a test file" txt
   ```

2. Generate multiple file formats at once:
   ```bash
   python3 text2file.py "Sample content for testing" txt md pdf jpg
   ```

3. Generate documentation with a longer text:
   ```bash
   python3 text2file.py "This is a sample document with multiple paragraphs. The text will be automatically wrapped to fit the output format. Great for creating test data!" md pdf
   ```

## Output

Generated files will be saved in the current working directory with names in the format:
```
generated_YYYYMMDD_HHMMSS.ext
```

## Adding New Formats

To add support for additional file formats:

1. Create a new function in `text2file.py` that generates the desired format
2. Update the `main()` function to handle the new extension
3. Add any new dependencies to `requirements.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
