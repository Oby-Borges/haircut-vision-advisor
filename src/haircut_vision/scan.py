"""Image checks and reviewable capture records; no depth or identity inference."""

import hashlib
import io

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

from .demo_fixture import demo_portrait, synthetic_landmarks
from .measurements import extract_measurements
from .vision import detect_landmarks


def load_capture(data):
    if not data or len(data) > 15 * 1024 * 1024:
        raise ValueError("Use a JPG or PNG smaller than 15 MB.")
    try:
        with Image.open(io.BytesIO(data)) as source:
            if source.width * source.height > 24_000_000:
                raise ValueError("Use an image smaller than 24 megapixels.")
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1600, 1600))
            return image
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("That file could not be read as a photo.") from exc


def assess_capture(image, view, *, synthetic=False):
    gray = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    brightness = float(gray.mean())
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    issues = []
    if min(image.size) < 240:
        issues.append("Move closer or use a photo at least 240 pixels on each side.")
    if brightness < 35 or brightness > 235:
        issues.append("Use even lighting; this image is too dark or too bright.")
    if sharpness < 12:
        issues.append("Hold still and retake; this image has very little sharp detail.")
    landmarks = None
    measurements = None
    if not issues and view == "front":
        landmarks = synthetic_landmarks() if synthetic else detect_landmarks(image)
        # MediaPipe normalizes x and y independently. Recover pixel geometry.
        points = [(x * image.width, y * image.height, z) for x, y, z in landmarks]
        measurements = extract_measurements(points)
        if measurements.yaw_asymmetry > 0.14:
            issues.append("Turn to face the camera directly, then retake the front view.")
    return {
        "image": image,
        "digest": hashlib.sha256(image.tobytes() + str(image.size).encode()).hexdigest(),
        "landmarks": landmarks,
        "measurements": measurements,
        "brightness": round(brightness, 1),
        "sharpness": round(sharpness, 1),
        "issues": issues,
        "reviewed": False,
        "synthetic": synthetic,
    }


def demo_view(view):
    if view == "front":
        return demo_portrait((600, 600))
    image = Image.new("RGB", (600, 600), "#e7ece8")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((230, 380, 370, 570), radius=50, fill="#c99e7b")
    if view in {"rear", "crown"}:
        draw.ellipse((150, 90, 450, 490), fill="#413e35")
        draw.arc((185, 130, 415, 430), 210, 330, fill="#8c8673", width=8)
    else:
        draw.ellipse((175, 105, 425, 465), fill="#d8a27f")
        draw.polygon([(390, 220), (465, 295), (390, 322)], fill="#d8a27f")
        draw.pieslice((165, 78, 435, 390), 150, 330, fill="#413e35")
        draw.ellipse((375, 222, 391, 240), fill="#273e37")
        if view == "right":
            image = ImageOps.mirror(image)
            draw = ImageDraw.Draw(image)
    draw.text((24, 24), f"SYNTHETIC / {view.upper()}", fill="#273e37")
    return image
