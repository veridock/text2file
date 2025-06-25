"""Tests for video file generation functionality."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the parent directory to the path so we can import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the module under test
from src.text2file.generators.video import (  # noqa: E402
    PILLOW_AVAILABLE,
    NUMPY_AVAILABLE,
    MOVIEPY_AVAILABLE,
    _create_video_frame,
    _generate_video_with_ffmpeg,
    _generate_video_with_moviepy,
    generate_video_file,
)

# Skip tests if required dependencies are not available
pytestmark = [
    pytest.mark.skipif(not PILLOW_AVAILABLE, reason="Pillow is required for video generation"),
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy is required for video generation"),
]


def test_create_video_frame():
    """Test creating a video frame with text."""
    if not PILLOW_AVAILABLE:
        pytest.skip("Pillow is not available")
        
    # Create a test frame
    frame = _create_video_frame("Test Frame", width=100, height=100)
    # Verify the frame was created with correct dimensions
    assert frame.size == (100, 100)
    assert frame.mode == "RGB"


@patch("subprocess.run")
def test_generate_video_with_ffmpeg(mock_run, tmp_path):
    """Test generating a video using ffmpeg."""
    # Mock the subprocess.run to simulate successful execution
    mock_run.return_value.returncode = 0
    
    output_path = tmp_path / "test_output.mp4"
    result = _generate_video_with_ffmpeg("Test Video", output_path, duration=1, fps=1)
    
    # Verify the function returns True on success
    assert result is True
    # Verify ffmpeg was called with the correct arguments
    assert mock_run.called
    
    # Test error case
    mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
    result = _generate_video_with_ffmpeg("Test Video", output_path)
    assert result is False


def test_generate_video_with_moviepy(tmp_path):
    """Test generating a video using moviepy."""
    if not MOVIEPY_AVAILABLE:
        pytest.skip("moviepy is not available")

    output_path = tmp_path / "test_output.mp4"

    # Mock moviepy classes to avoid actual video generation
    with (
        patch("moviepy.editor.TextClip") as mock_text_cls,
        patch("moviepy.editor.ColorClip") as mock_color_cls,
        patch("moviepy.editor.CompositeVideoClip") as mock_composite_cls,
    ):
        # Setup mock behavior
        mock_text = MagicMock()
        mock_text_cls.return_value = mock_text

        mock_color = MagicMock()
        mock_color_cls.return_value = mock_color

        mock_composite = MagicMock()
        mock_composite_cls.return_value = mock_composite

        # Call the function
        result = _generate_video_with_moviepy(
            "Test Video", output_path, duration=1, fps=24
        )

        # Verify the function returns True on success
        assert result is True

        # Verify the mocks were called correctly
        mock_text_cls.assert_called_once()
        mock_color_cls.assert_called_once()
        mock_composite_cls.assert_called_once()
        mock_composite.write_videofile.assert_called_once()


def test_generate_video_file(tmp_path):
    """Test the main video file generation function."""
    output_path = tmp_path / "test_output.mp4"

    # Test with mock for ffmpeg
    with (
        patch("src.text2file.generators.video._generate_video_with_ffmpeg") \
        as mock_ffmpeg,
        patch("src.text2file.generators.video._generate_video_with_moviepy") \
        as mock_moviepy,
    ):
        # Test ffmpeg success
        mock_ffmpeg.return_value = True
        result = generate_video_file("Test Video", output_path)
        assert result == output_path
        mock_ffmpeg.assert_called_once()

        # Test fallback to moviepy
        mock_ffmpeg.return_value = False
        mock_moviepy.return_value = True
        result = generate_video_file("Test Video", output_path)
        assert result == output_path
        mock_moviepy.assert_called_once()

    # Test error case when no backend is available
    with (
        patch(
            "src.text2file.generators.video._generate_video_with_ffmpeg",
            return_value=False,
        ),
        patch(
            "src.text2file.generators.video._generate_video_with_moviepy",
            return_value=False,
        ),
        pytest.raises(RuntimeError),
    ):
        generate_video_file("Test Video", output_path)


def test_video_generator_registration():
    """Test that the video generator is properly registered."""
    from src.text2file.generators.registration import get_generator

    # Check that the generator is registered for supported extensions
    for ext in ["mp4", "avi", "mov", "mkv"]:
        generator = get_generator(ext)
        assert generator is not None, f"No generator found for extension: {ext}"
        assert callable(generator), f"Generator for {ext} is not callable"


if __name__ == "__main__":
    pytest.main(["-v", __file__])  # pragma: no cover
