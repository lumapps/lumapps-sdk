from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from .translation import Translations


@dataclass(frozen=True)
class Article:
    id: UUID
    author_id: UUID

    created_at: datetime

    title: Translations
    short: Translations
