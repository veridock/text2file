#!/usr/bin/env python3
"""Test script to verify video generation dependencies."""


def test_imports():
    print("Testing video generation imports...")

    # Test PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont

        print("✅ PIL/Pillow is available")
    except ImportError as e:
        print(f"❌ PIL/Pillow import failed: {e}")

    # Test NumPy
    try:
        import numpy as np

        print(f"✅ NumPy is available (v{np.__version__})")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")

    # Test MoviePy
    try:
        from moviepy.editor import TextClip, CompositeVideoClip, ImageClip

        print("✅ MoviePy is available")
    except ImportError as e:
        print(f"❌ MoviePy import failed: {e}")

    # Test OpenCV
    try:
        import cv2

        print(f"✅ OpenCV is available (v{cv2.__version__})")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")


if __name__ == "__main__":
    test_imports()
