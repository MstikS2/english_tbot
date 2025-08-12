from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from core.constants import MAX_NAME_LEN


class NamedModelMixin:
    """The mixin for db models that adds id and name columns."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(MAX_NAME_LEN))
