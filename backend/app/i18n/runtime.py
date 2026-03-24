import gettext
from pathlib import Path

from collections.abc import Callable
from contextvars import ContextVar
from functools import lru_cache

DOMAIN = "messages"
LOCALES_DIR = Path(__file__).parent / "locales"

_current_gettext: ContextVar[Callable[[str], str] | None] = ContextVar(
    "current_gettext", default=None
)


def _(msg: str) -> str:
    fn = _current_gettext.get()
    return fn(msg) if fn else msg


def activate(locale: str):
    tr = get_translation(locale)
    return _current_gettext.set(tr.gettext)


def deactivate(token) -> None:
    _current_gettext.reset(token)


@lru_cache
def get_translation(locale: str) -> gettext.GNUTranslations:
    return gettext.translation(
        DOMAIN, localedir=LOCALES_DIR, languages=[locale], fallback=True
    )
