"""Generators for video file formats."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

# Check if Pillow is available
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Check if NumPy is available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from ..generators.registration import register_generator_directly


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

            # Generate frames
            frame_paths = []
            for i in range(duration * fps):
                frame_text = f"{text}\n\nFrame {i+1}/{duration * fps}"
                frame = _create_video_frame(frame_text)
                frame_path = temp_dir_path / f"frame_{i:04d}.png"
                frame.save(frame_path)
                frame_paths.append(frame_path)

            # Use ffmpeg to create video from frames
            ffmpeg_cmd = [
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
                "-vf",
                f"fps={fps}",
                str(output_path),
            ]

            # Run ffmpeg
            result = subprocess.run(
                ffmpeg_cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return False

            return True

    except Exception as e:
        print(f"Error generating video: {e}")
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
        from moviepy.editor import CompositeVideoClip, ImageClip, TextClip
        from moviepy.video.fx.all import fadein, fadeout

        # Create a text clip
        txt_clip = TextClip(
            text,
            fontsize=40,
            color="white",
            bg_color="black",
            size=(1280, 720),
            method="caption",
        ).set_duration(duration)

        # Add fade in/out effects
        txt_clip = fadein(txt_clip, 0.5).crossfadeout(0.5)

        # Set the FPS
        txt_clip.fps = fps

        # Write the video file
        txt_clip.write_videofile(
            str(output_path), codec="libx264", audio=False, fps=fps, logger=None
        )

        return True

    except ImportError:
        return False
    except Exception as e:
        print(f"Error generating video with moviepy: {e}")
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
            "NumPy is required for video generation. "
            "Install with: pip install numpy"
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
    
    raise RuntimeError(
        "Failed to generate video. Make sure you have either moviepy or ffmpeg installed.\n"
        "Install with: pip install moviepy numpy pillow\n"
        "Or install ffmpeg: https://ffmpeg.org/download.html"
        "Video generation failed. Please check that you have ffmpeg installed "
        "and available in your system PATH."
    )


# Register the video generator if dependencies are available
if PILLOW_AVAILABLE and NUMPY_AVAILABLE:
    from .registration import register_generator_directly
    register_generator_directly(["mp4", "avi", "mov"], generate_video_file)
elif __name__ == "__main__":
    # Print warnings if running as a script
    if not PILLOW_AVAILABLE:
        print("Warning: Pillow is not installed. Video generation will not be available.")
    if not NUMPY_AVAILABLE:
        print("Warning: NumPy is not installed. Video generation will not be available.")
