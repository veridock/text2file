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
    _video_not_available,
)

# Test parameters
TEST_VIDEO_TEXT = "Test Video Content"
TEST_VIDEO_DURATION = 2  # Shorter duration for faster tests
TEST_VIDEO_FPS = 24
TEST_VIDEO_RESOLUTION = (640, 480)  # Smaller resolution for faster tests
TEST_BG_COLOR = "#0000ff"  # Blue
TEST_TEXT_COLOR = "#ffff00"  # Yellow
TEST_FONT_SIZE = 36

# Skip tests if required dependencies are not available
pytestmark = [
    pytest.mark.skipif(
        not PILLOW_AVAILABLE, reason="Pillow is required for video generation"
    ),
    pytest.mark.skipif(
        not NUMPY_AVAILABLE, reason="NumPy is required for video generation"
    ),
]


@pytest.mark.parametrize(
    "width,height,expected_size",
    [
        (100, 100, (100, 100)),
        (640, 480, (640, 480)),
        (1920, 1080, (1920, 1080)),
    ],
)
def test_create_video_frame(width, height, expected_size):
    """Test creating video frames with different dimensions."""
    if not PILLOW_AVAILABLE:
        pytest.skip("Pillow is not available")

    # Create a test frame
    frame = _create_video_frame(
        "Test Frame",
        width=width,
        height=height,
        bg_color=TEST_BG_COLOR,
        text_color=TEST_TEXT_COLOR,
        font_size=TEST_FONT_SIZE,
    )

    # Verify the frame was created with correct dimensions and properties
    assert frame.size == expected_size
    assert frame.mode == "RGB"


@pytest.mark.parametrize(
    "duration,fps",
    [
        (1, 1),
        (5, 24),
        (10, 30),
    ],
)
@patch("subprocess.run")
def test_generate_video_with_ffmpeg(mock_run, tmp_path, duration, fps):
    """Test generating videos with ffmpeg using different parameters."""
    # Mock the subprocess.run to simulate successful execution
    mock_run.return_value.returncode = 0

    output_path = tmp_path / f"test_output_{duration}s_{fps}fps.mp4"

    # Call with test parameters
    result = _generate_video_with_ffmpeg(
        text=TEST_VIDEO_TEXT, output_path=output_path, duration=duration, fps=fps
    )

    # Verify the function returns True on success
    assert result is True
    assert mock_run.called

    # Verify the output file path was used in the command
    assert str(output_path) in " ".join(mock_run.call_args[0][0])


@patch("subprocess.run")
def test_generate_video_with_ffmpeg_errors(mock_run, tmp_path):
    """Test error handling in ffmpeg video generation."""
    # Test CalledProcessError
    mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
    output_path = tmp_path / "test_error.mp4"
    result = _generate_video_with_ffmpeg(TEST_VIDEO_TEXT, output_path)
    assert result is False

    # Test FileNotFoundError
    mock_run.side_effect = FileNotFoundError("ffmpeg not found")
    result = _generate_video_with_ffmpeg(TEST_VIDEO_TEXT, output_path)
    assert result is False


@pytest.mark.parametrize(
    "duration,fps",
    [
        (1, 1),
        (5, 24),
        (10, 30),
    ],
)
@patch("moviepy.editor.TextClip")
@patch("moviepy.editor.ImageClip")
@patch("moviepy.editor.CompositeVideoClip")
@patch("moviepy.video.VideoClip.ColorClip")
@patch("src.text2file.generators.video._create_video_frame")
def test_generate_video_with_moviepy(
    mock_create_frame,
    mock_color_cls,
    mock_composite_cls,
    mock_image_cls,
    mock_text_cls,
    tmp_path,
    duration,
    fps,
    monkeypatch,
):
    """Test generating videos with moviepy using different parameters."""
    if not MOVIEPY_AVAILABLE:
        pytest.skip("moviepy is not available")
            
    print("\n=== TEST SETUP ===")
    print(f"Mock TextClip: {mock_text_cls}")
    print(f"Mock ImageClip: {mock_image_cls}")
    print(f"Mock CompositeVideoClip: {mock_composite_cls}")
    print(f"Mock ColorClip: {mock_color_cls}")
    print(f"Mock _create_video_frame: {mock_create_frame}")

    output_path = tmp_path / f"test_moviepy_{duration}s_{fps}fps.mp4"

    # Create a mock PIL Image with required attributes and methods
    mock_pil_image = MagicMock()
    mock_pil_image.size = (1280, 720)
    # Make convert() return the same mock
    mock_pil_image.convert.return_value = mock_pil_image
    mock_create_frame.return_value = mock_pil_image

    # Setup mock behavior for TextClip
    mock_text_clip = MagicMock()
    # Set up method chaining for TextClip methods
    mock_text_clip.set_duration.return_value = mock_text_clip
    # Set the size attribute
    mock_text_clip.size = (1280, 720)
    # Mock the TextClip class to return our mock instance
    mock_text_cls.return_value = mock_text_clip

    # Setup mock behavior for ImageClip
    mock_image_clip = MagicMock()
    # Set up method chaining for ImageClip methods
    mock_image_clip.set_duration.return_value = mock_image_clip
    # Set the size attribute
    mock_image_clip.size = (1280, 720)
    # Mock the ImageClip class to return our mock instance
    mock_image_cls.return_value = mock_image_clip

    # Setup mock behavior for ColorClip
    mock_color_clip = MagicMock()
    # Set the size attribute that will be accessed
    mock_color_clip.size = (1280, 720)
    # Set up method chaining for set_duration
    mock_color_clip.set_duration.return_value = mock_color_clip
    # Mock the ColorClip class to return our mock instance
    mock_color_cls.return_value = mock_color_clip
    print(f"\n=== MOCK COLOR CLIP SETUP ===")
    print(f"Mock ColorClip class: {mock_color_cls}")
    print(f"Mock ColorClip instance: {mock_color_clip}")
    print(f"Mock ColorClip size: {mock_color_clip.size}")
        
    # Debug: Print the actual ColorClip class being used by CompositeVideoClip
    from moviepy.editor import CompositeVideoClip
    from moviepy.video.VideoClip import ColorClip
    print(f"\n=== ACTUAL IMPORTS ===")
    print(f"Actual CompositeVideoClip: {CompositeVideoClip}")
    print(f"Actual ColorClip: {ColorClip}")
    print(f"Is ColorClip patched? {ColorClip is mock_color_cls}")
    print(f"Is CompositeVideoClip patched? {CompositeVideoClip is mock_composite_cls}")
        
    # Add a side effect to the mock to see when it's called
    def color_clip_side_effect(*args, **kwargs):
        print("\n=== COLOR CLIP CREATED ===")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")
        mock_color_clip._args = args
        mock_color_clip._kwargs = kwargs
        return mock_color_clip
            
    mock_color_cls.side_effect = color_clip_side_effect

    # Create a custom mock class for CompositeVideoClip
    class MockCompositeVideoClip:
        def __init__(self, clips, size=None, bg_color=None, **kwargs):
            self.clips = clips
            self.size = size or (1280, 720)
            self.bg_color = bg_color
            # Create a mock background clip with the correct size
            self.bg = MagicMock()
            self.bg.size = self.size
            self.bg.get_frame.return_value = None
            self.bg.close.return_value = None
            self.created_bg = True
            self.duration = max((getattr(c, "duration", 0) for c in clips), default=10)
            self.fps = 24

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs):
            pass

        def write_videofile(self, *args, **kwargs):
            return None

        def close(self):
            pass

        def __iter__(self):
            return iter([])

        def __len__(self):
            return len(self.clips)

        def __getitem__(self, key):
            return self

        def __setitem__(self, key, value):
            pass

        def is_playing(self, t):
            return True

        def set_duration(self, duration):
            self.duration = duration
            return self

        def set_fps(self, fps):
            self.fps = fps
            return self

    # Set up the mock to use our custom class
    mock_composite = MockCompositeVideoClip([])
    mock_composite_cls.side_effect = MockCompositeVideoClip

    # Mock the close methods for other clips
    mock_text_clip.close.return_value = None
    mock_image_clip.close.return_value = None

    # Call with test parameters
    print("\n=== CALLING _generate_video_with_moviepy ===")
    try:
        result = _generate_video_with_moviepy(
            text=TEST_VIDEO_TEXT, output_path=output_path, duration=duration, fps=fps
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")
        raise

    # Verify the function returns True on success
    assert result is True

    # Verify the mocks were called with expected parameters
    mock_create_frame.assert_called_once_with(TEST_VIDEO_TEXT, width=1280, height=720)
    mock_pil_image.convert.assert_called_once_with("RGB")

    # Verify TextClip was created with correct parameters
    mock_text_cls.assert_called_once_with(
        txt=TEST_VIDEO_TEXT, fontsize=70, color="white", size=(1280, 720)
    )
    mock_text_clip.set_duration.assert_called_once_with(duration)

    # Verify ImageClip was created with the frame
    mock_image_cls.assert_called_once_with(mock_pil_image)
    mock_image_clip.set_duration.assert_called_once_with(duration)

    # Verify CompositeVideoClip was created with correct layers
    mock_composite_cls.assert_called_once_with([mock_image_clip, mock_text_clip])

    # Verify write_videofile was called with correct parameters
    mock_composite.write_videofile.assert_called_once_with(
        str(output_path), fps=fps, codec="libx264", audio=False
    )


@patch("moviepy.editor.TextClip")
def test_generate_video_with_moviepy_errors(mock_text_cls, tmp_path):
    """Test error handling in moviepy video generation."""
    if not MOVIEPY_AVAILABLE:
        pytest.skip("moviepy is not available")

    output_path = tmp_path / "test_error.mp4"

    # Test with exception during text clip creation
    mock_text_cls.side_effect = Exception("Test error")
    result = _generate_video_with_moviepy(TEST_VIDEO_TEXT, output_path)
    assert result is False


@pytest.mark.parametrize("format_ext", ["mp4", "avi", "mov", "mkv"])
def test_generate_video_file_formats(tmp_path, format_ext):
    """Test video file generation with different output formats."""
    output_path = tmp_path / f"test_video.{format_ext}"

    with patch(
        "src.text2file.generators.video._generate_video_with_ffmpeg", return_value=True
    ) as mock_ffmpeg, patch(
        "src.text2file.generators.video._generate_video_with_moviepy",
        return_value=False,
    ) as mock_moviepy:
        # Test successful generation
        result = generate_video_file(
            content=TEST_VIDEO_TEXT,
            output_path=output_path,
            duration=TEST_VIDEO_DURATION,
            fps=TEST_VIDEO_FPS,
            width=TEST_VIDEO_RESOLUTION[0],
            height=TEST_VIDEO_RESOLUTION[1],
            bg_color=TEST_BG_COLOR,
            text_color=TEST_TEXT_COLOR,
            font_size=TEST_FONT_SIZE,
        )

        assert result is True
        mock_ffmpeg.assert_called_once_with(
            TEST_VIDEO_TEXT, output_path, TEST_VIDEO_DURATION, TEST_VIDEO_FPS
        )
        mock_moviepy.assert_not_called()


def test_generate_video_file_fallback(tmp_path):
    """Test fallback from ffmpeg to moviepy."""
    output_path = tmp_path / "test_fallback.mp4"

    with (
        patch(
            "src.text2file.generators.video._generate_video_with_ffmpeg",
            return_value=False,
        ) as mock_ffmpeg,
        patch(
            "src.text2file.generators.video._generate_video_with_moviepy",
            return_value=True,
        ) as mock_moviepy,
    ):
        result = generate_video_file(
            content=TEST_VIDEO_TEXT,
            output_path=output_path,
            use_moviepy=False,  # Should still try ffmpeg first due to this being False
        )

        assert result is True
        mock_ffmpeg.assert_called_once_with(
            TEST_VIDEO_TEXT, output_path, 5, 24  # Default duration  # Default FPS
        )
        mock_moviepy.assert_called_once_with(
            TEST_VIDEO_TEXT, output_path, 5, 24  # Default duration  # Default FPS
        )


def test_generate_video_file_errors(tmp_path):
    """Test error conditions in video file generation."""
    output_path = tmp_path / "test_error.mp4"

    # Test with no backends available
    with (
        patch(
            "src.text2file.generators.video._generate_video_with_ffmpeg",
            return_value=False,
        ) as mock_ffmpeg,
        patch(
            "src.text2file.generators.video._generate_video_with_moviepy",
            return_value=False,
        ) as mock_moviepy,
    ):
        with pytest.raises(RuntimeError, match="Failed to generate video"):
            generate_video_file(content=TEST_VIDEO_TEXT, output_path=output_path)

        mock_ffmpeg.assert_called_once()
        mock_moviepy.assert_called_once()

    # Test with invalid parameters - these will fail at the frame generation level
    # rather than parameter validation, so we don't expect ValueErrors here
    # The actual video generation will fail in _create_video_frame if parameters are invalid


@pytest.mark.parametrize(
    "ext,expected",
    [
        ("mp4", True),
        ("avi", True),
        ("mov", True),
        ("mkv", True),
        ("webm", False),  # Not supported
        ("wmv", False),  # Not supported
    ],
)
def test_video_generator_registration(ext, expected):
    """Test that the video generator is properly registered for supported formats."""
    from src.text2file.generators.registration import get_generator

    generator = get_generator(ext)

    if expected:
        assert generator is not None, f"No generator found for extension: {ext}"
        assert callable(generator), f"Generator for {ext} is not callable"
        # Verify it's not the error handler function
        assert generator is not _video_not_available
    else:
        assert (
            generator is None or generator is _video_not_available
        ), f"Unexpected generator found for unsupported extension: {ext}"


def test_video_not_available_error():
    """Test the error message when video generation is not available."""
    with pytest.raises(ImportError) as exc_info:
        _video_not_available()

    assert "Video generation requires additional dependencies" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main(["-v", __file__])  # pragma: no cover
