"""Generators for video file formats.

This module provides functionality to generate video files with text content.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

# Check if Pillow is available
try:
    from PIL import Image, ImageDraw, ImageFont  # noqa: F401

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Check if NumPy is available
try:
    import numpy as np  # type: ignore

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Check if moviepy is available
try:
    from moviepy.editor import CompositeVideoClip, ImageClip, TextClip  # type: ignore

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    CompositeVideoClip = ImageClip = TextClip = None

# Conditional import to avoid circular imports
if TYPE_CHECKING or (PILLOW_AVAILABLE and NUMPY_AVAILABLE):
    from ..generators.registration import register_generator_directly  # noqa: F401


def _create_video_frame(
    text: str,
    width: int = 1280,
    height: int = 720,
    bg_color: str = "white",
    text_color: str = "black",
) -> Image.Image:
    """Create a single video frame with centered text.

    Args:
        text: Text to display on the frame
        width: Frame width in pixels
        height: Frame height in pixels
        bg_color: Background color
        text_color: Text color

    Returns:
        PIL Image containing the frame
    """
    # Create a blank image with the specified background color
    frame = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(frame)

    # Get a font - try to use a system font, fall back to default
    try:
        font_size = 40
        font = ImageFont.truetype("Arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size and position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position to center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text
    draw.text((x, y), text, fill=text_color, font=font)

    return frame


def _generate_video_with_ffmpeg(
    text: str, output_path: Path, duration: int = 5, fps: int = 24
) -> bool:
    """Generate a video file using ffmpeg.

    Args:
        text: Text to display in the video
        output_path: Path to save the video
        duration: Duration of the video in seconds
        fps: Frames per second

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Create frames using Pillow
            for i in range(duration * fps):
                frame = _create_video_frame(text)
                frame_path = temp_dir_path / f"frame_{i:04d}.png"
                frame.save(frame_path, "PNG")

            # Use ffmpeg to create the video
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-framerate",
                str(fps),
                "-i",
                str(temp_dir_path / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(output_path),
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error generating video with ffmpeg: {e}", file=sys.stderr)
        return False


def _generate_video_with_moviepy(
    text: str, output_path: Path, duration: int = 5, fps: int = 24
) -> bool:
    """Generate a video file using moviepy.

    Args:
        text: Text to display in the video
        output_path: Path to save the video
        duration: Duration of the video in seconds
        fps: Frames per second

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from moviepy.editor import (  # type: ignore
            CompositeVideoClip,
            ImageClip,
            TextClip,
        )

        # Create a text clip
        txt_clip = TextClip(
            text,
            fontsize=70,
            color="white",
            size=(1280, 720),
        ).set_duration(duration)

        # Create a color clip for the background
        color_clip = ImageClip(
            _create_video_frame(text).convert("RGB")  # type: ignore
        ).set_duration(duration)

        # Overlay the text clip on the color clip
        video = CompositeVideoClip([color_clip, txt_clip])  # type: ignore

        # Write the video file
        video.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio=False,
        )
        return True

    except ImportError as e:
        print(f"MoviePy not available: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(
            f"Error generating video with MoviePy: {e}",
            file=sys.stderr,
        )
        return False


def generate_video_file(
    content: str, output_path: Path, duration: int = 5, fps: int = 24
) -> Path:
    """Generate a video file with the given content.

    Args:
        content: Text content to display in the video
        output_path: Path where the video should be saved
        duration: Duration of the video in seconds
        fps: Frames per second

    Returns:
        Path to the generated video file

    Raises:
        ImportError: If required dependencies are not installed
        RuntimeError: If video generation fails
    """
    if not PILLOW_AVAILABLE:
        raise ImportError(
            "Pillow is required for video generation. "
            "Install with: pip install pillow"
        )

    if not NUMPY_AVAILABLE:
        raise ImportError(
            "NumPy is required for video generation. " "Install with: pip install numpy"
        )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Try moviepy first
    try:
        if _generate_video_with_moviepy(content, output_path, duration, fps):
            return output_path
    except ImportError as e:
        print(f"Note: {e}", file=sys.stderr)

    # Fall back to ffmpeg if moviepy fails or is not available
    try:
        if _generate_video_with_ffmpeg(content, output_path, duration, fps):
            return output_path
    except Exception as e:
        print(f"FFmpeg error: {e}", file=sys.stderr)
        error_msg = (
            "Failed to generate video. Make sure you have either moviepy or ffmpeg "
            "installed.\nInstall with: pip install moviepy numpy pillow\n"
            "Or install ffmpeg: https://ffmpeg.org/download.html\n"
            "Video generation failed. Please check that you have ffmpeg installed "
            "and available in your system PATH."
        )
        raise RuntimeError(error_msg) from e


# Register the video generator if dependencies are available
if PILLOW_AVAILABLE and NUMPY_AVAILABLE:
    register_generator_directly(  # type: ignore
        ["mp4", "avi", "mov", "mkv"],
        generate_video_file,
        requires=["Pillow", "numpy"],
        description="Generate video files with text content",
    )
else:
    # Register a placeholder that will raise an informative error
    register_generator_directly(  # type: ignore
        ["mp4", "avi", "mov", "mkv"],
        None,
        requires=["Pillow", "numpy"],
        description="Generate video files with text content "
        "(requires Pillow and numpy)",
    )
