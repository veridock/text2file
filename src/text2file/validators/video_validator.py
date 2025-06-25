"""Validators for video file formats."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from ..generators.base import BaseGenerator
from .base import BaseValidator, ValidationResult

# Try to import OpenCV for video validation
HAS_OPENCV = False
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    pass

# Try to import ffprobe for more detailed video info
HAS_FFPROBE = bool(subprocess.run(['which', 'ffprobe'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE).returncode == 0)

class VideoValidator(BaseValidator):
    """Base validator for video files."""
    
    # Expected format for this validator (should be overridden by subclasses)
    FORMAT: Optional[str] = None
    
    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a video file.
        
        Args:
            file_path: Path to the video file to validate
            
        Returns:
            ValidationResult indicating whether the video is valid
        """
        try:
            # First check if the file exists and is readable
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    message=f"File not found: {file_path}"
                )
                
            if not path.is_file():
                return ValidationResult(
                    is_valid=False,
                    message=f"Not a file: {file_path}"
                )
                
            # Check file extension matches expected format
            if cls.FORMAT and not path.name.lower().endswith(f".{cls.FORMAT.lower()}"):
                return ValidationResult(
                    is_valid=False,
                    message=f"Expected {cls.FORMAT.upper()} file, got {path.suffix}"
                )
            
            # Try to validate with OpenCV first
            if HAS_OPENCV:
                result = cls._validate_with_opencv(file_path)
                if result.is_valid:
                    return result
            
            # Fall back to ffprobe if available
            if HAS_FFPROBE:
                result = cls._validate_with_ffprobe(file_path)
                if result.is_valid:
                    return result
            
            # If we get here, we couldn't validate the video
            return ValidationResult(
                is_valid=False,
                message="Could not validate video (missing dependencies: install OpenCV or ffmpeg)",
                details={
                    "opencv_available": HAS_OPENCV,
                    "ffprobe_available": HAS_FFPROBE,
                    "size": path.stat().st_size
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating video file: {str(e)}",
                details={"error": str(e)}
            )
    
    @classmethod
    def _validate_with_opencv(cls, file_path: str) -> ValidationResult:
        """Validate a video file using OpenCV."""
        if not HAS_OPENCV:
            return ValidationResult(
                is_valid=False,
                message="OpenCV is not available"
            )
            
        try:
            # Open the video file
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                return ValidationResult(
                    is_valid=False,
                    message="Could not open video file with OpenCV"
                )
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Try to read the first frame
            ret, frame = cap.read()
            if not ret:
                return ValidationResult(
                    is_valid=False,
                    message="Could not read any frames from the video"
                )
            
            # Release the video capture object
            cap.release()
            
            return ValidationResult(
                is_valid=True,
                message=f"Valid video: {width}x{height} @ {fps:.2f} fps, {frame_count} frames",
                details={
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "validated_with": "opencv"
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating with OpenCV: {str(e)}",
                details={"error": str(e)}
            )
    
    @classmethod
    def _validate_with_ffprobe(cls, file_path: str) -> ValidationResult:
        """Validate a video file using ffprobe."""
        if not HAS_FFPROBE:
            return ValidationResult(
                is_valid=False,
                message="ffprobe is not available"
            )
            
        try:
            # Run ffprobe to get video information
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name,width,height,r_frame_rate,duration,nb_frames',
                '-show_entries', 'format=format_name,duration,size',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
            
            if result.returncode != 0:
                return ValidationResult(
                    is_valid=False,
                    message=f"ffprobe error: {result.stderr.strip()}"
                )
            
            # Parse the JSON output
            info = json.loads(result.stdout)
            
            if not info.get('streams') or not info['streams']:
                return ValidationResult(
                    is_valid=False,
                    message="No video streams found in the file"
                )
            
            # Get video stream info
            video_stream = info['streams'][0]
            format_info = info.get('format', {})
            
            # Calculate FPS from r_frame_rate (e.g., "30/1" -> 30.0)
            fps = 0.0
            if 'r_frame_rate' in video_stream:
                try:
                    num, denom = map(float, video_stream['r_frame_rate'].split('/'))
                    if denom > 0:
                        fps = num / denom
                except (ValueError, ZeroDivisionError):
                    pass
            
            # Get frame count and duration
            frame_count = int(video_stream.get('nb_frames', 0))
            duration = float(video_stream.get('duration', 0))
            
            # If duration is not available in stream, try format
            if duration <= 0 and 'duration' in format_info:
                duration = float(format_info['duration'])
            
            # If frame count is not available, estimate from duration and FPS
            if frame_count <= 0 and duration > 0 and fps > 0:
                frame_count = int(duration * fps)
            
            return ValidationResult(
                is_valid=True,
                message=f"Valid {video_stream.get('codec_name', 'video')}: "
                       f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)} @ {fps:.2f} fps",
                details={
                    "codec": video_stream.get('codec_name', 'unknown'),
                    "width": video_stream.get('width'),
                    "height": video_stream.get('height'),
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "format": format_info.get('format_name', '').split(',')[0],
                    "size": int(format_info.get('size', 0)),
                    "validated_with": "ffprobe"
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating with ffprobe: {str(e)}",
                details={"error": str(e)}
            )


class Mp4Validator(VideoValidator):
    """Validator for MP4 video files."""
    FORMAT = "mp4"


class AviValidator(VideoValidator):
    """Validator for AVI video files."""
    FORMAT = "avi"


class MovValidator(VideoValidator):
    """Validator for QuickTime MOV video files."""
    FORMAT = "mov"


class MkvValidator(VideoValidator):
    """Validator for Matroska MKV video files."""
    FORMAT = "mkv"


class WebmValidator(VideoValidator):
    """Validator for WebM video files."""
    FORMAT = "webm"


class FlvValidator(VideoValidator):
    """Validator for Flash Video FLV files."""
    FORMAT = "flv"


class WmvValidator(VideoValidator):
    """Validator for Windows Media Video WMV files."""
    FORMAT = "wmv"


class MpegValidator(VideoValidator):
    """Validator for MPEG video files."""
    FORMAT = "mpeg"


class M4vValidator(VideoValidator):
    """Validator for M4V video files."""
    FORMAT = "m4v"


class ThreeGpValidator(VideoValidator):
    """Validator for 3GP video files."""
    FORMAT = "3gp"


class MtsValidator(VideoValidator):
    """Validator for MTS video files (AVCHD)."""
    FORMAT = "mts"


class M2tsValidator(VideoValidator):
    """Validator for M2TS video files (Blu-ray)."""
    FORMAT = "m2ts"


class VobValidator(VideoValidator):
    """Validator for VOB video files (DVD)."""
    FORMAT = "vob"


class AsfValidator(VideoValidator):
    """Validator for ASF video files."""
    FORMAT = "asf"

class SwfValidator(VideoValidator):
    """Validator for SWF (Shockwave Flash) files."""
    FORMAT = "swf"

class MpgValidator(VideoValidator):
    """Validator for MPG video files."""
    FORMAT = "mpg"

class MpeValidator(VideoValidator):
    """Validator for MPE video files."""
    FORMAT = "mpe"

class M2vValidator(VideoValidator):
    """Validator for M2V video files."""
    FORMAT = "m2v"

class TsValidator(VideoValidator):
    """Validator for TS (MPEG Transport Stream) video files."""
    FORMAT = "ts"

class MxfValidator(VideoValidator):
    """Validator for MXF video files."""
    FORMAT = "mxf"

class OggValidator(VideoValidator):
    """Validator for OGG video files."""
    FORMAT = "ogg"

class OgvValidator(VideoValidator):
    """Validator for OGV video files."""
    FORMAT = "ogv"

class F4vValidator(VideoValidator):
    """Validator for F4V video files."""
    FORMAT = "f4v"

class MjpegValidator(VideoValidator):
    """Validator for MJPEG video files."""
    FORMAT = "mjpeg"

class Mj2Validator(VideoValidator):
    """Validator for MJ2 video files."""
    FORMAT = "mj2"

class DvValidator(VideoValidator):
    """Validator for DV video files."""
    FORMAT = "dv"

class H261Validator(VideoValidator):
    """Validator for H.261 video files."""
    FORMAT = "h261"

class H263Validator(VideoValidator):
    """Validator for H.263 video files."""
    FORMAT = "h263"

class H264Validator(VideoValidator):
    """Validator for H.264 video files."""
    FORMAT = "h264"

class H265Validator(VideoValidator):
    """Validator for H.265/HEVC video files."""
    FORMAT = "h265"

class HevcValidator(VideoValidator):
    """Validator for HEVC video files (same as H.265)."""
    FORMAT = "hevc"

class Vp8Validator(VideoValidator):
    """Validator for VP8 video files."""
    FORMAT = "vp8"

class Vp9Validator(VideoValidator):
    """Validator for VP9 video files."""
    FORMAT = "vp9"

class Av1Validator(VideoValidator):
    """Validator for AV1 video files."""
    FORMAT = "av1"

class TheoraValidator(VideoValidator):
    """Validator for Theora video files."""
    FORMAT = "ogv"  # Theora is typically in OGV/OGG containers

class ProresValidator(VideoValidator):
    """Validator for Apple ProRes video files."""
    FORMAT = "mov"  # ProRes is typically in MOV containers

class DnxhdValidator(VideoValidator):
    """Validator for DNxHD video files."""
    FORMAT = "mxf"  # DNxHD is often in MXF containers

class CineformValidator(VideoValidator):
    """Validator for CineForm video files."""
    FORMAT = "avi"  # CineForm is often in AVI containers

class AnimationValidator(VideoValidator):
    """Validator for Animation video files."""
    FORMAT = "mov"  # Animation codec is typically in MOV containers

class LagarithValidator(VideoValidator):
    """Validator for Lagarith video files."""
    FORMAT = "avi"  # Lagarith is typically in AVI containers

class UtVideoValidator(VideoValidator):
    """Validator for Ut Video files."""
    FORMAT = "avi"  # Ut Video is typically in AVI containers

class HapValidator(VideoValidator):
    """Validator for HAP video files."""
    FORMAT = "mov"  # HAP is typically in MOV containers

class NotchlcValidator(VideoValidator):
    """Validator for NotchLC video files."""
    FORMAT = "mov"  # NotchLC is typically in MOV containers

class SheervideoValidator(VideoValidator):
    """Validator for SheerVideo files."""
    FORMAT = "avi"  # SheerVideo is typically in AVI containers
