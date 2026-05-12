import uuid
import shutil
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = _PROJECT_ROOT / "img" / "produk"

IMAGE_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)"


def pick_image_file(parent=None) -> str | None:
    home = str(Path.home())
    path, _ = QFileDialog.getOpenFileName(
        parent, "Pilih Foto Produk", home, IMAGE_FILTER
    )
    return path if path else None


def save_image_to_app(source_path: str) -> str | None:
    if not source_path:
        return None
    src = Path(source_path)
    if not src.is_file():
        return None

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    ext = src.suffix or ".png"
    dest_name = f"{uuid.uuid4().hex}{ext}"
    dest = IMAGE_DIR / dest_name

    shutil.copy2(src, dest)
    return f"produk/{dest_name}"


def load_product_pixmap(gambar: str | None, size: tuple[int, int] = (160, 160)) -> QPixmap | None:
    if not gambar:
        return None
    img_path = _PROJECT_ROOT / "img" / gambar
    if not img_path.is_file():
        return None
    pixmap = QPixmap(str(img_path))
    if pixmap.isNull():
        return None
    return pixmap.scaled(
        size[0], size[1],
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )


def delete_image_file(gambar: str | None) -> None:
    if not gambar:
        return
    img_path = _PROJECT_ROOT / "img" / gambar
    if img_path.is_file():
        img_path.unlink(missing_ok=True)