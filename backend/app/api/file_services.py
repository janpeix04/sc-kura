import os
import re
import hashlib
import shutil

from datetime import datetime
from pathlib import Path
from typing import BinaryIO


_filename_ascii_strip = re.compile(r"[^A-Za-z0-9_.-]")


def secure_filename(filename: str) -> str:
    """
    From Werkzeug secure_filename
    """
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    normalized_filename = _filename_ascii_strip.sub("", "_".join(filename.split()))
    filename = str(normalized_filename).strip("._")
    return filename


class FileSystemStorage:
    """
    File system storage which stores files in the local filesystem
    """

    OVERWRITE_EXISTING_FILES = True
    default_chunk_size = 64 * 1024

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)

    def get_name(self, name: str) -> str:
        """
        Get the normalized name of the file
        """
        return secure_filename(Path(name).name)

    def get_path(self, name: str) -> str:
        """
        Get full path to the file
        """
        return str(self._path / Path(name))

    def get_size(self, name: str) -> int:
        """
        Get the size in bytes
        """
        return (self._path / name).stat().st_size

    def open(self, name: str) -> BinaryIO:
        """
        Open a file of the file object in binary mode
        """
        path = self.get_path(name)
        return open(path, "rb")

    def write(self, file: BinaryIO, name: str) -> str:
        """
        Write input file which is openend in a binary mode to destination
        """
        filename = self.get_name(name)
        path = self.get_path(filename)

        file.seek(0, 0)
        with open(path, "wb") as output:
            while True:
                chunk = file.read(self.default_chunk_size)
                if not chunk:
                    break
                output.write(chunk)
        return str(path)

    def delete(self, name: str) -> None:
        """
        Delete the file from the filesystem
        """
        Path(self.get_path(name)).unlink()

    def exists(self, name: str) -> bool:
        """
        Check if the file exists in the filesystem
        """
        return Path(self.get_path(name)).exists()

    def generate_new_filename(self, filename: str) -> str:
        counter = 0
        path = self._path / filename
        stem, extension = Path(filename).stem, Path(filename).suffix

        while path.exists():
            counter += 1
            path = self._path / f"{stem}_{counter} {extension}"

        return path.name

    def generate_filename(self, filename: str, user_id: str) -> str:
        ext = Path(filename).suffix

        hash = hashlib.sha256(f"{filename}_{user_id}".encode()).hexdigest()[:16]

        timestamp = datetime.now().strftime("%y-%m-%d_%H-%M-%S")

        new_filename = datetime.today().strftime(f"{timestamp}_{user_id}_{hash}{ext}")
        return new_filename


class StorageFile(str):
    """
    Represents a file stored using a given storage backend
    """

    def __new__(cls, name: str, storage: FileSystemStorage) -> "StorageFile":
        return str.__new__(cls, storage.get_path(name))

    def __init__(self, *, name: str, storage: FileSystemStorage):
        self._name = name
        self._storage = storage

    @property
    def name(self) -> str:
        return self._storage.get_name(self._name)

    @property
    def path(self) -> str:
        return self._storage.get_path(self._name)

    @property
    def size(self) -> int:
        return self._storage.get_size(self._name)

    def open(self) -> BinaryIO:
        return self._storage.open(self._name)

    def write(self, file: BinaryIO, user_id: str | None = None) -> str:
        if user_id is not None:
            self._name = self._storage.generate_filename(
                filename=self._name, user_id=user_id
            )
        if not self._storage.OVERWRITE_EXISTING_FILES:
            self._name = self._storage.generate_new_filename(self._name)
        return self._storage.write(file=file, name=self._name)

    def delete(self) -> None:
        return self._storage.delete(self._name)

    def exists(self) -> bool:
        return self._storage.exists(self._name)

    def __str__(self) -> str:
        return self.path


def extract_folders_from_filename(filename: str) -> list[str]:
    parts = filename.split("/")
    if len(parts) <= 1:
        return None
    return parts[:-1]


def get_parent_path(path: str, current_path: str) -> str:
    parts = path.split("/")
    if len(parts) <= 1:
        return current_path
    return "/" + "/".join(parts[:-1])


def get_hard_diks_space(path: str = "/") -> int:
    return shutil.disk_usage(path=path).total
