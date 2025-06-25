"""Tests for the text2file package."""

import tempfile
from pathlib import Path
from unittest import TestCase

from text2file.generators import SUPPORTED_EXTENSIONS, generate_file


class TestText2File(TestCase):
    """Test cases for the text2file package."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_content = "This is a test content for text2file testing."

    def tearDown(self):
        """Clean up test environment."""
        # Remove all files in the test directory
        for item in self.test_dir.glob("*"):
            if item.is_file():
                item.unlink()
        self.test_dir.rmdir()

    def test_supported_extensions(self):
        """Test that we have generators for all supported extensions."""
        # Check that we have at least some supported extensions
        self.assertGreater(len(SUPPORTED_EXTENSIONS), 0)

        # Check that common formats are supported
        for ext in ["txt", "md", "pdf", "jpg", "png", "docx", "xlsx", "zip"]:
            self.assertIn(ext, SUPPORTED_EXTENSIONS)

    def test_generate_text_file(self):
        """Test generating a text file."""
        output_path = generate_file(
            self.test_content, "txt", self.test_dir, "test"
        )
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".txt")
        self.assertEqual(
            output_path.read_text(encoding="utf-8").strip(), self.test_content
        )

    def test_generate_markdown_file(self):
        """Test generating a markdown file."""
        markdown_content = "# Test\n\nThis is a **test** markdown file."
        output_path = generate_file(
            markdown_content, "md", self.test_dir, "test"
        )
        self.assertTrue(output_path.exists())
        self.assertIn(output_path.suffix, [".md", ".markdown"])
        self.assertEqual(
            output_path.read_text(encoding="utf-8").strip(), markdown_content
        )

    def test_generate_pdf_file(self):
        """Test generating a PDF file."""
        try:
            output_path = generate_file(
                self.test_content, "pdf", self.test_dir, "test"
            )
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.suffix, ".pdf")
            self.assertGreater(output_path.stat().st_size, 0)
        except ImportError:
            self.skipTest("fpdf2 not installed, skipping PDF test")

    def test_generate_image_file(self):
        """Test generating an image file."""
        for ext in ["jpg", "png"]:
            with self.subTest(ext=ext):
                output_path = generate_file(
                    self.test_content, ext, self.test_dir, f"test_{ext}"
                )
                self.assertTrue(output_path.exists())
                self.assertEqual(output_path.suffix, f".{ext}")
                self.assertGreater(output_path.stat().st_size, 0)

    def test_generate_office_file(self):
        """Test generating office files."""
        for ext in ["docx", "xlsx"]:
            with self.subTest(ext=ext):
                try:
                    output_path = generate_file(
                        self.test_content, ext, self.test_dir, f"test_{ext}"
                    )
                    self.assertTrue(output_path.exists())
                    self.assertEqual(output_path.suffix, f".{ext}")
                    self.assertGreater(output_path.stat().st_size, 0)
                except ImportError:
                    self.skipTest(f"Required package for {ext} not installed")

    def test_generate_archive_file(self):
        """Test generating archive files."""
        # Test with supported archive formats
        for ext in ["zip", "tar.gz", "tgz"]:
            with self.subTest(ext=ext):
                output_path = generate_file(
                    self.test_content,
                    ext,
                    self.test_dir,
                    f"test_{ext.replace('.', '_')}",
                )
                self.assertTrue(output_path.exists())
                # Check for valid extensions (.zip, .tar.gz, .tgz)
                if ext == "tar.gz":
                    self.assertEqual("".join(output_path.suffixes), ".tar.gz")
                elif ext == "tgz":
                    self.assertEqual(output_path.suffix, ".tgz")
                else:
                    self.assertEqual(output_path.suffix, f".{ext}")
                self.assertGreater(output_path.stat().st_size, 0)
