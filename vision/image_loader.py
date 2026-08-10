"""Loading and validating uploaded mission layout images."""

from __future__ import annotations

import io

import numpy as np
from PIL import Image, UnidentifiedImageError

SUPPORTED_FORMATS = ("PNG", "JPEG", "JPG", "BMP")
MIN_IMAGE_DIMENSION = 32
MAX_IMAGE_DIMENSION = 4096


class ImageLoadError(ValueError):
    """Raised when uploaded bytes cannot be decoded into a usable layout image."""


def load_image(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded file bytes into an RGB ``np.ndarray``.

    Args:
        file_bytes: Raw bytes from a Streamlit ``UploadedFile``.

    Returns:
        An ``(H, W, 3)`` uint8 array.

    Raises:
        ImageLoadError: if the bytes cannot be decoded, the format is
            unsupported, or the resulting image fails :func:`validate_image`.
    """
    try:
        with Image.open(io.BytesIO(file_bytes)) as pil_image:
            image_format = (pil_image.format or "").upper()
            if image_format not in SUPPORTED_FORMATS:
                raise ImageLoadError(
                    f"Unsupported image format {image_format!r}. "
                    f"Supported formats: {', '.join(SUPPORTED_FORMATS)}."
                )
            array = np.array(pil_image.convert("RGB"), dtype=np.uint8)
    except UnidentifiedImageError as exc:
        raise ImageLoadError("Could not decode the uploaded file as an image.") from exc

    if not validate_image(array):
        raise ImageLoadError(
            "Image failed validation: both dimensions must be between "
            f"{MIN_IMAGE_DIMENSION} and {MAX_IMAGE_DIMENSION} pixels."
        )
    return array


def validate_image(image: np.ndarray) -> bool:
    """Check that an image array is a well-formed RGB image within size limits."""
    if image.ndim != 3 or image.shape[2] != 3:
        return False
    height, width = image.shape[:2]
    if height < MIN_IMAGE_DIMENSION or width < MIN_IMAGE_DIMENSION:
        return False
    if height > MAX_IMAGE_DIMENSION or width > MAX_IMAGE_DIMENSION:
        return False
    return True
