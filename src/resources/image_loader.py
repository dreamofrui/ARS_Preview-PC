"""
Image Loader
Handles loading and caching of images
"""

from pathlib import Path
from typing import List, Optional
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QObject, pyqtSignal


class ImageLoader(QObject):
    """Loads and caches images"""

    images_loaded = pyqtSignal(int)  # Emitted when images are loaded

    def __init__(self, parent=None):
        super().__init__(parent)
        self._normal_images: List[Path] = []
        self._wait_image: Optional[QPixmap] = None
        self._timeout_images: List[Path] = []
        self._cache: dict[Path, QPixmap] = {}

    def load_normal_images(self, directory: Path) -> int:
        """Load normal images from directory"""
        self._normal_images.clear()

        if not directory.exists():
            return 0

        # Support common image formats
        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

        for path in sorted(directory.iterdir()):
            if path.suffix.lower() in extensions:
                self._normal_images.append(path)

        self.images_loaded.emit(len(self._normal_images))
        return len(self._normal_images)

    def load_wait_image(self, path: Path) -> bool:
        """Load wait image"""
        if not path.exists():
            return False

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return False

        self._wait_image = pixmap
        return True

    def load_timeout_images(self, directory: Path) -> int:
        """Load timeout images from directory"""
        self._timeout_images.clear()

        if not directory.exists():
            return 0

        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

        for path in sorted(directory.iterdir()):
            if path.suffix.lower() in extensions:
                self._timeout_images.append(path)

        return len(self._timeout_images)

    def get_normal_image(self, index: int) -> Optional[QPixmap]:
        """Get normal image by index (with cycling)"""
        if not self._normal_images:
            return None

        actual_index = index % len(self._normal_images)
        path = self._normal_images[actual_index]

        # Check cache first
        if path in self._cache:
            return self._cache[path]

        # Load and cache
        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            self._cache[path] = pixmap

        return pixmap

    def get_wait_image(self) -> Optional[QPixmap]:
        """Get wait image"""
        return self._wait_image

    def get_timeout_image(self, index: int = 0) -> Optional[QPixmap]:
        """Get timeout image by index (with cycling)"""
        if not self._timeout_images:
            return self.get_wait_image()

        actual_index = index % len(self._timeout_images)
        path = self._timeout_images[actual_index]

        if path in self._cache:
            return self._cache[path]

        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            self._cache[path] = pixmap

        return pixmap

    def get_random_timeout_image(self) -> Optional[QPixmap]:
        """Get random timeout image"""
        import random
        if not self._timeout_images:
            return self.get_wait_image()

        path = random.choice(self._timeout_images)
        if path in self._cache:
            return self._cache[path]

        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            self._cache[path] = pixmap

        return pixmap

    @property
    def normal_image_count(self) -> int:
        """Get count of normal images"""
        return len(self._normal_images)

    @property
    def timeout_image_count(self) -> int:
        """Get count of timeout images"""
        return len(self._timeout_images)

    def clear_cache(self) -> None:
        """Clear image cache"""
        self._cache.clear()
