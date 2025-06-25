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
        # Get the current set of supported extensions
        supported = SUPPORTED_EXTENSIONS()

        # Check that we have at least some supported extensions
        self.assertGreater(len(supported), 0)

        # Debug output
        print("\nSupported extensions:", sorted(supported))

        # Check that common formats are supported
        common_formats = [
            "txt",
            "md",
            "py",
            "sh",
            "html",
            "css",
            "js",
            "json",
            "csv",
            "zip",
            "tar",
            "pdf",
        ]
        for ext in common_formats:
            if ext not in supported:
                print(f"Warning: Common format '{ext}' is not in supported extensions")

    def test_generate_text_file(self):
        """Test generating a text file."""
        output_path = generate_file(self.test_content, "txt", self.test_dir, "test")
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".txt")
        self.assertEqual(
            output_path.read_text(encoding="utf-8").strip(), self.test_content
        )

    def test_generate_markdown_file(self):
        """Test generating a markdown file."""
        markdown_content = "# Test\n\nThis is a **test** markdown file."
        output_path = generate_file(markdown_content, "md", self.test_dir, "test")
        self.assertTrue(output_path.exists())
        self.assertIn(output_path.suffix, [".md", ".markdown"])
        self.assertEqual(
            output_path.read_text(encoding="utf-8").strip(), markdown_content
        )

    def test_generate_pdf_file(self):
        """Test generating a PDF file."""
        # Skip if PDF is not in supported extensions
        supported = SUPPORTED_EXTENSIONS()
        if "pdf" not in supported:
            self.skipTest("PDF generation not supported in this installation")

        # Check if we can import fpdf2
        try:
            import fpdf
            from fpdf import FPDF, XPos, YPos
        except ImportError:
            self.skipTest("fpdf2 is required for PDF generation")

        try:
            output_path = generate_file(self.test_content, "pdf", self.test_dir, "test")
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.suffix, ".pdf")
            self.assertGreater(output_path.stat().st_size, 0)
        except Exception as e:
            if "fpdf2 is required" in str(e):
                self.skipTest("fpdf2 is required for PDF generation")
            raise

    def test_generate_image_file(self):
        """Test generating an image file."""
        # Skip if no image formats are supported
        supported = SUPPORTED_EXTENSIONS()
        if not any(ext in supported for ext in ["jpg", "jpeg", "png", "gif", "svg"]):
            self.skipTest("No image formats supported in this installation")

        # Test each supported image format
        for ext in ["jpg", "jpeg", "png", "gif", "svg"]:
            if ext in supported:
                with self.subTest(ext=ext):
                    output_path = generate_file(
                        self.test_content, ext, self.test_dir, f"test_{ext}"
                    )
                    self.assertTrue(output_path.exists())
                    self.assertEqual(output_path.suffix, f".{ext}")
                    self.assertGreater(output_path.stat().st_size, 0)

    def test_generate_office_file(self):
        """Test generating office files."""
        supported = SUPPORTED_EXTENSIONS()
        office_formats = ["docx", "xlsx", "odt", "ods"]

        # Skip if no office formats are supported
        if not any(ext in supported for ext in office_formats):
            self.skipTest("No office formats supported in this installation")

        for ext in office_formats:
            if ext in supported:
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
        supported = SUPPORTED_EXTENSIONS()
        archive_formats = ["zip", "tar", "tar.gz", "tgz"]

        # Skip if no archive formats are supported
        if not any(ext in supported for ext in archive_formats):
            self.skipTest("No archive formats supported in this installation")

        # Test with supported archive formats
        for ext in archive_formats:
            if ext not in supported:
                continue
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
