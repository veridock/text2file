"""Command-line interface for text2file."""

import click
from pathlib import Path
from typing import List, Optional

from .generators import SUPPORTED_EXTENSIONS, generate_file


@click.command()
@click.argument("content")
@click.argument("extensions", nargs=-1, required=True)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    default=Path.cwd(),
    help="Output directory for generated files",
)
@click.option(
    "--prefix",
    "-p",
    type=str,
    default="generated",
    help="Prefix for generated filenames",
)
@click.version_option()
def cli(content: str, extensions: List[str], output_dir: Path, prefix: str) -> None:
    """Generate test files with the given content and extensions.

    Examples:
        text2file "Test content" txt md pdf
        text2file "Another test" --output-dir ./output --prefix test docx xlsx
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate extensions
    invalid_exts = [ext for ext in extensions if ext.lower() not in SUPPORTED_EXTENSIONS]
    if invalid_exts:
        raise click.UsageError(
            f"Unsupported extensions: {', '.join(invalid_exts)}. "
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    
    # Generate files
    generated_files = []
    for ext in extensions:
        try:
            filepath = generate_file(content, ext, output_dir, prefix)
            click.echo(f"Generated: {filepath}")
            generated_files.append(filepath)
        except Exception as e:
            click.echo(f"Error generating {ext} file: {e}", err=True)
    
    if generated_files:
        click.echo("\nSuccessfully generated files:")
        for filepath in generated_files:
            click.echo(f"- {filepath}")
    else:
        click.echo("No files were generated.")
