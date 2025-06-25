"""Generators for archive file formats."""

import os
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from ..generators import register_generator


def _create_sample_files(content: str, temp_dir: Path) -> None:
    """Create sample files to include in the archive.

    Args:
        content: Text content to include in the files
        temp_dir: Directory to create the files in
    """
    # Create a simple text file
    (temp_dir / "sample.txt").write_text(content, encoding="utf-8")

    # Create a simple CSV file
    csv_content = "name,value\n"
    for i, line in enumerate(content.split("\n")[:5], 1):
        csv_content += f"{line.strip()},{i}\n"
    (temp_dir / "data.csv").write_text(csv_content, encoding="utf-8")

    # Create a simple JSON file
    json_content = {
        "title": "Sample Data",
        "content": content.split("\n")[0],
        "items": [
            {"id": i, "text": line} for i, line in enumerate(content.split("\n")[:3], 1)
        ],
    }
    import json

    (temp_dir / "data.json").write_text(
        json.dumps(json_content, indent=2), encoding="utf-8"
    )


@register_generator(["zip"])
def generate_zip_file(content: str, output_path: Path) -> Path:
    """Generate a ZIP file with sample files containing the given content.

    Args:
        content: Text content to include in the archive
        output_path: Path where the ZIP file should be saved

    Returns:
        Path to the generated ZIP file
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        _create_sample_files(content, temp_dir)

        # Create a ZIP file
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)

    return output_path


@register_generator(["tar", "tar.gz", "tgz"])
def generate_tar_file(content: str, output_path: Path) -> Path:
    """Generate a TAR file with sample files containing the given content.

    Args:
        content: Text content to include in the archive
        output_path: Path where the TAR file should be saved

    Returns:
        Path to the generated TAR file
    """
    # Determine compression mode based on extension
    ext = output_path.suffix.lower()
    if ext in (".gz", ".tgz"):
        mode = "w:gz"
    else:
        mode = "w"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        _create_sample_files(content, temp_dir)

        # Create a TAR file
        with tarfile.open(output_path, mode) as tarf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    tarf.add(file_path, arcname=arcname)

    return output_path
