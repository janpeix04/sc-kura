import platform
import shutil
from datetime import datetime

from app.models import File, Folder


def score(item: File | Folder, now: datetime) -> int:
    hours_opened = (now - item.opened_at).total_seconds() / 3600
    hours_modified = (now - item.modified_at).total_seconds() / 3600
    hours_created = (now - item.created_at).total_seconds() / 3600

    return (
        (0.5 / (hours_opened + 1))
        + (0.3 / (hours_modified + 1))
        + (0.2 / (hours_created + 1))
    )


def get_total_disk_space() -> int:
    system = platform.system()

    if system == "Windows":
        path = "C:\\"
    else:
        path = "/"

    return shutil.disk_usage(path).total
