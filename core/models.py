from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from core.constants import MAX_NAME_LEN


class IdModelMixin:
    """The mixin for db models that adds id column."""
    id: Mapped[int] = mapped_column(primary_key=True)


class NamedModelMixin(IdModelMixin):
    """The mixin for db models that adds id and name columns."""

    name: Mapped[Optional[str]] = mapped_column(String(MAX_NAME_LEN))
