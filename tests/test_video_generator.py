"""Tests for video generation functionality."""
import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
from PIL import Image as PILImage

# Import the video module to test
from text2file.generators.video import (
    _create_video_frame,
    _generate_video_with_ffmpeg,
    _generate_video_with_moviepy,
    _video_not_available,
    generate_video_file,
)

# Add the parent directory to the path so we can import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the module under test
with patch('text2file.generators.video._create_video_frame') as mock_create_frame:
    from text2file.generators.video import (
        PILLOW_AVAILABLE,
        NUMPY_AVAILABLE,
        MOVIEPY_AVAILABLE,
    )
    
    # Create a mock PIL Image with required attributes and methods
    mock_pil_image = MagicMock()
    mock_pil_image.size = (1280, 720)
    # Make convert() return the same mock
    mock_pil_image.convert.return_value = mock_pil_image
    # Setup the mock to return our mock PIL image when called with the test text
    mock_create_frame.return_value = mock_pil_image
    
    # Reset the mock call count since it might have been called during imports
    mock_create_frame.reset_mock()

# Apply patches for the test
with (
    patch('text2file.generators.video.PILLOW_AVAILABLE', True),
    patch('text2file.generators.video.NUMPY_AVAILABLE', True),
    patch('text2file.generators.video.MOVIEPY_AVAILABLE', True),
    patch('text2file.generators.video.Image', PILImage),
    patch('text2file.generators.video.np', MagicMock()),
):
    # Re-import to apply patches
    import importlib
    importlib.reload(sys.modules['text2file.generators.video'])
    from text2file.generators.video import _create_video_frame  # noqa: F401

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
        (None, None, (640, 480)),  # Test default values (matches implementation)
    ],
)
def test_create_video_frame(width, height, expected_size):
    """Test _create_video_frame with different dimensions."""
    from text2file.generators.video import _create_video_frame
    
    # Create a mock frame with the expected attributes
    class MockImage:
        def __init__(self, size, mode, color):
            self.size = size
            self.mode = str(mode)  # Ensure mode is always a string
            self.color = color
        
        def __eq__(self, other):
            return (isinstance(other, MockImage) and 
                   self.size == other.size and 
                   self.mode == other.mode and 
                   self.color == other.color)
    
    # Create the expected frame with the expected size
    expected_frame = MockImage(expected_size, "RGB", TEST_BG_COLOR)
    
    # Patch the necessary modules
    with patch('PIL.Image.new') as mock_new, \
         patch('PIL.ImageDraw.Draw') as mock_draw, \
         patch('PIL.ImageFont.load_default') as mock_load_default, \
         patch('PIL.ImageFont.truetype') as mock_truetype:
        
        # Reset all mocks to ensure clean state
        mock_new.reset_mock()
        mock_draw.reset_mock()
        mock_load_default.reset_mock()
        mock_truetype.reset_mock()
        
        # Set up the mock for Image.new to return our test frame
        mock_new.return_value = expected_frame
        
        # Prepare the arguments for the function call
        kwargs = {
            "text": "Test",
            "bg_color": TEST_BG_COLOR,
            "text_color": TEST_TEXT_COLOR,
            "font_size": TEST_FONT_SIZE
        }
        
        # Add width/height if provided (None tests defaults)
        if width is not None and height is not None:
            kwargs["width"] = width
            kwargs["height"] = height
        
        # Call the function
        frame = _create_video_frame(**kwargs)
        
        # Verify the frame has the expected properties
        assert frame.size == expected_size, f"Expected size {expected_size}, got {frame.size}"
        assert isinstance(frame.mode, str), "frame.mode should be a string"
        assert frame.mode == "RGB"
        
        # Verify Image.new was called with the correct arguments
        expected_size_arg = (width if width is not None else 640, 
                           height if height is not None else 480)
        mock_new.assert_called_once_with("RGB", expected_size_arg, TEST_BG_COLOR)


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
    args, _ = mock_run.call_args
    assert str(output_path) in " ".join(args[0])


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


# Import the module first to avoid import-time side effects
import text2file.generators.video as video_module

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
def test_generate_video_with_moviepy(
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
    print("\n=== TEST STARTING ===")
    if not MOVIEPY_AVAILABLE:
        pytest.skip("moviepy is not available")
            
    print("\n=== TEST SETUP ===")
    print(f"Mock TextClip: {mock_text_cls}")
    print(f"Mock ImageClip: {mock_image_cls}")
    print(f"Mock CompositeVideoClip: {mock_composite_cls}")
    print(f"Mock ColorClip: {mock_color_cls}")

    output_path = tmp_path / f"test_moviepy_{duration}s_{fps}fps.mp4"
    print(f"\n=== TEST PARAMETERS ===")
    print(f"Output path: {output_path}")
    print(f"Duration: {duration}s")
    print(f"FPS: {fps}")
    
    # Patch _create_video_frame in the module where it's being used
    with patch('text2file.generators.video._create_video_frame') as mock_create_frame:
        print(f"Mock _create_video_frame: {mock_create_frame}")

        # Create a mock PIL Image with required attributes and methods
        mock_pil_image = MagicMock()
        mock_pil_image.size = (1280, 720)
        # Make convert() return the same mock
        mock_pil_image.convert.return_value = mock_pil_image
        # Setup the mock to return our mock PIL image when called with the test text
        mock_create_frame.return_value = mock_pil_image
        
        # Reset the mock call count since it might have been called during imports
        mock_create_frame.reset_mock()

    # Setup mock behavior for TextClip
    mock_text_clip = MagicMock()
    # Set up method chaining for TextClip methods
    mock_text_clip.set_duration.return_value = mock_text_clip
    # Set the size attribute
    mock_text_clip.size = (1280, 720)
    # Mock the TextClip class to return our mock instance
    mock_text_cls.return_value = mock_text_clip

    # Setup mock behavior for ImageClip
    def image_clip_side_effect(*args, **kwargs):
        # Create a new mock for each ImageClip instance
        mock_img_clip = MagicMock()
        # Set up method chaining for ImageClip methods
        mock_img_clip.set_duration.return_value = mock_img_clip
        # Set the size attribute
        mock_img_clip.size = (1280, 720)
        
        # If the first argument is a PIL Image, add shape attribute
        if args and hasattr(args[0], 'size'):
            img = args[0]
            # Mock the shape attribute that MoviePy looks for
            mock_img_clip.img = img
            mock_img_clip.shape = (*img.size[::-1], 3)  # (height, width, channels)
        
        return mock_img_clip
    
    # Set up the mock to use our side effect
    mock_image_cls.side_effect = image_clip_side_effect
    mock_image_clip = mock_image_cls.return_value  # For backward compatibility

    # Setup mock behavior for ColorClip
    print("\n=== SETTING UP COLOR CLIP MOCK ===")
    mock_color_clip = MagicMock()
    # Set the size attribute that will be accessed
    mock_color_clip.size = (1280, 720)
    # Set up method chaining for set_duration
    mock_color_clip.set_duration.return_value = mock_color_clip
    # Mock the ColorClip class to return our mock instance
    mock_color_cls.return_value = mock_color_clip
    print(f"ColorClip mock created with size: {mock_color_clip.size}")
    print(f"\n=== MOCK COLOR CLIP SETUP ===")
    print(f"Mock ColorClip class: {mock_color_cls}")
    print(f"Mock ColorClip instance: {mock_color_clip}")
    print(f"Mock ColorClip size: {mock_color_clip.size}")
        
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
    print("\n=== CREATING MOCK COMPOSITE VIDEO CLIP ===")
        
    class MockCompositeVideoClip:
        def __init__(self, clips, **kwargs):
            print("\n=== MOCK COMPOSITE VIDEO CLIP ===")
            print(f"Clips: {clips}")
            print(f"Kwargs: {kwargs}")
            self.clips = clips
            self.duration = 0.0  # Default duration
            self.size = (1280, 720)  # Default size
            self.fps = 24  # Default FPS
            # Create a mock for write_videofile
            self.write_videofile = MagicMock(return_value=None)
            self.close = MagicMock(return_value=None)
    
        def set_duration(self, duration):
            print(f"Setting duration to {duration}")
            self.duration = float(duration)  # Ensure duration is a number
            return self
    
        def __enter__(self):
            print("Entering MockCompositeVideoClip context")
            return self
    
        def __exit__(self, *args, **kwargs):
            print("Exiting MockCompositeVideoClip context")
    
        def __iter__(self):
            return iter(self.clips)
    
        def __len__(self):
            return len(self.clips)
    
        def __getitem__(self, key):
            return self.clips[key]
    
        def __setitem__(self, key, value):
            self.clips[key] = value
    
        def is_playing(self, t):
            return True
    
        def set_fps(self, fps):
            self.fps = fps
            return self

    # Set up the mock to use our custom class
    print("\n=== SETTING UP COMPOSITE VIDEO CLIP MOCK ===")
    mock_composite = MockCompositeVideoClip([])
    mock_composite.write_videofile.return_value = None
    mock_composite.close.return_value = None
    mock_composite_cls.side_effect = MockCompositeVideoClip
    print(f"Mock CompositeVideoClip class set up with side_effect: {mock_composite_cls.side_effect}")
        
    # Add a side effect to the mock to log when it's called
    def composite_side_effect(*args, **kwargs):
        print("\n=== COMPOSITE VIDEO CLIP CREATED ===")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")
        instance = MockCompositeVideoClip(*args, **kwargs)
        print(f"Created MockCompositeVideoClip instance: {instance}")
        return instance
            
    mock_composite_cls.side_effect = composite_side_effect

    # Mock the close methods for other clips
    mock_text_clip.close.return_value = None
    mock_image_clip.close.return_value = None

    # Import the module first to avoid import-time side effects
    import importlib
    print("\n=== RELOADING VIDEO MODULE ===")
    importlib.reload(video_module)
        
    # Get the function we want to test
    print("\n=== GETTING FUNCTION TO TEST ===")
    func_to_test = video_module._generate_video_with_moviepy
    print(f"Function to test: {func_to_test}")
    print(f"Function module: {func_to_test.__module__}")
    print(f"Mock create frame: {mock_create_frame}")
        
    # Call with test parameters
    print("\n=== CALLING _generate_video_with_moviepy ===")
    print(f"Text: {TEST_VIDEO_TEXT}")
    print(f"Output path: {output_path}")
    print(f"Duration: {duration}, FPS: {fps}")
        
    # Call the function
    print("\n=== CALLING FUNCTION ===")
    print(f"Mock create frame call count before: {mock_create_frame.call_count}")
    print(f"Mock create frame calls: {mock_create_frame.mock_calls}")
    
    result = func_to_test(
        text=TEST_VIDEO_TEXT,
        output_path=output_path,
        duration=duration,
        fps=fps
    )
    
    print(f"\n=== AFTER FUNCTION CALL ===")
    print(f"Mock create frame call count after: {mock_create_frame.call_count}")
    print(f"Mock create frame calls: {mock_create_frame.mock_calls}")
    print(f"Result from _generate_video_with_moviepy: {result}")

    # Verify the function returns True on success
    assert result is True

    # Verify the mocks were called with expected parameters
    mock_create_frame.assert_called_once()
    
    # Verify TextClip creation
    mock_text_cls.assert_called_once()
    text_clip_args, text_clip_kwargs = mock_text_cls.call_args
    assert text_clip_kwargs.get('txt') == TEST_VIDEO_TEXT
    assert text_clip_kwargs.get('color') == 'white'
    
    # Verify duration was set on text clip
    if hasattr(mock_text_clip.set_duration, 'assert_called_once'):
        mock_text_clip.set_duration.assert_called_once_with(duration)
    
    # Verify ColorClip was created with correct size
    mock_color_cls.assert_called_once()
    
    # Verify CompositeVideoClip was created with both clips
    mock_composite_cls.assert_called_once()
    composite_args, _ = mock_composite_cls.call_args
    assert len(composite_args[0]) == 2  # Should have 2 clips
    
    # Verify write_videofile was called
    mock_composite.write_videofile.assert_called_once()
    write_args, write_kwargs = mock_composite.write_videofile.call_args
    assert str(output_path) in write_args[0]  # Output path should be first arg
    assert write_kwargs.get('fps') == fps
    assert write_kwargs.get('codec') == 'libx264'


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
