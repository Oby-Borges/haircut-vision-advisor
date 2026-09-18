"""Haircut Vision Advisor core package."""

from .catalog import load_catalog
from .face_shape import classify_face_shape
from .recommend import rank_hairstyles

__all__ = ["classify_face_shape", "load_catalog", "rank_hairstyles"]
__version__ = "0.1.0"
