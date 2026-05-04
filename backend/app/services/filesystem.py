import uuid
import hashlib

from pathlib import Path
from typing import BinaryIO


class FileSystemStorage:
    """File system storage which stores files in the local filesystem."""

    OVERWRITE_EXISTING_FILES = True
    default_chunk_size = 64 * 1024

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)

    def get_name(self, name: str) -> str:
        """Get the normalized name of the file."""
        return Path(name).name

    def get_path(self, name: str) -> str:
        """Get full path of the file."""
        return str(self._path / Path(name))

    def get_size(self, name: str) -> str:
        """Get the size in bytes."""
        return (self._path / Path(name)).stat().st_size

    def get_mime_type(self, name: str) -> str:
        """Get mime type of the file."""
        return Path(name).suffix

    def open(self, name: str) -> BinaryIO:
        """Open a file of the file object in binary mode."""
        path = self.get_path(name)
        return open(path, "rb")

    def write(self, file: BinaryIO, name: str) -> str:
        """Write input file which is openend in a binary mode to destionation."""
        filename = self.get_name(name)
        path = self.get_path(filename)

        file.seek(0, 0)
        with open(path, "wb") as output:
            while True:
                chunk = file.read(self.default_chunk_size)
                if not chunk:
                    break
                output.write(chunk)

        return path

    def delete(self, name: str) -> None:
        """Delete the file from the filesystem."""
        Path(self.get_path(name)).unlink()

    def exists(self, name: str) -> bool:
        """Check if the file exists in the filesystem"""
        return Path(self.get_path(name)).exists()

    def generate_new_file(self, filename: str) -> str:
        counter = 0
        path = self._path / filename
        stem, extension = Path(filename).stem, Path(filename).suffix

        while path.exists():
            counter += 1
            path = self._path / f"{stem}_{counter}{extension}"

        return path.name

    def generate_filename(
        self, filename: str, user_id: uuid.UUID, folder_id: uuid.UUID
    ) -> str:
        ext = Path(filename).suffix
        hash = hashlib.sha256(f"{filename}".encode()).hexdigest()

        new_filename = f"{user_id}_{hash}_{folder_id}{ext}"

        return new_filename


class StorageFile(str):
    """Represents a file stored using a given storage backend."""

    def __new__(cls, name: str, storage: FileSystemStorage) -> "StorageFile":
        return str.__new__(cls, storage.get_path(name))

    def __init__(self, *, name: str, storage: FileSystemStorage):
        self._name = name
        self._storage = storage

        self._storage_id: uuid.UUID | None = None

    @property
    def name(self) -> str:
        return self._storage.get_name(self._name)

    @property
    def path(self):
        return self._storage.get_path(self._name)

    @property
    def size(self):
        return self._storage.get_size(self._name)

    @property
    def mime_type(self):
        return self._storage.get_mime_type(self._name)

    @property
    def storage_id(self) -> uuid.UUID | None:
        """
        Stable identifier for DB storage reference.
        This is NOT the filename.
        """
        return self._storage_id

    def exists(self):
        return self._storage.exists(self._name)

    def open(self) -> BinaryIO:
        return self._storage.open(self._name)

    def delete(self) -> None:
        self._storage.delete(self._name)

    def write(
        self,
        file: BinaryIO,
        user_id: uuid.UUID | None = None,
        folder_id: uuid.UUID | None = None,
        storage_id: uuid.UUID | None = None,
    ) -> str:
        if user_id is not None and folder_id is not None:
            self._name = self._storage.generate_filename(self._name, user_id, folder_id)
        if not self._storage.OVERWRITE_EXISTING_FILES:
            self._name = self._storage.generate_new_file(self._name)
        if storage_id is not None:
            self._storage_id = str(storage_id)
        return self._storage.write(file, self._name)
