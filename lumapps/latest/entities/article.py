from dataclasses import dataclass
from datetime import datetime

from .translation import Translations


@dataclass(frozen=True)
class Article:
    id: str
    author_id: str

    created_at: datetime

    title: Translations
    short: Translations
