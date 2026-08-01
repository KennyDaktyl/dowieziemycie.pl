"""Shared image processing for anything an admin uploads through an
ImageField. Every upload goes through the same pipeline — WebP (smaller,
no visible quality loss at ~82%), resized to a sane max, plus a separate
thumbnail for gallery photos — so there's no "did I remember to optimize
this one" gap depending on which model happens to hold it.
"""

import io
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

FULL_MAX_SIZE = (1920, 1920)
THUMBNAIL_MAX_SIZE = (480, 480)
WEBP_QUALITY = 82


def _render_webp(raw: bytes, max_size: tuple[int, int]) -> ContentFile:
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)  # respect phone camera orientation
    if img.mode == "CMYK":
        img = img.convert("RGB")
    img.thumbnail(max_size, Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
    return ContentFile(buffer.getvalue())


def is_already_processed(name: str | None) -> bool:
    """Our own pipeline always names its output *.webp — a plain save() with
    no new file assigned (e.g. editing just a caption) keeps that name, so
    this is a safe, simple way to avoid reprocessing on every save()."""
    return bool(name) and name.lower().endswith(".webp")


def process_cover_image(instance, field_name: str) -> None:
    """Convert a single cover/hero image field to WebP in place. Call from
    the model's save() before super().save()."""
    field_file = getattr(instance, field_name)
    if not field_file or is_already_processed(field_file.name):
        return
    field_file.seek(0)
    raw = field_file.read()
    stem = Path(field_file.name).stem
    content = _render_webp(raw, FULL_MAX_SIZE)
    field_file.save(f"{stem}.webp", content, save=False)


def process_gallery_photo(instance, image_field_name: str, thumbnail_field_name: str) -> None:
    """Convert a gallery photo to WebP and (re)generate its thumbnail. Call
    from the model's save() before super().save()."""
    field_file = getattr(instance, image_field_name)
    if not field_file or is_already_processed(field_file.name):
        return
    field_file.seek(0)
    raw = field_file.read()
    stem = Path(field_file.name).stem

    full_content = _render_webp(raw, FULL_MAX_SIZE)
    field_file.save(f"{stem}.webp", full_content, save=False)

    thumb_content = _render_webp(raw, THUMBNAIL_MAX_SIZE)
    getattr(instance, thumbnail_field_name).save(f"{stem}_thumb.webp", thumb_content, save=False)
