from sqlalchemy import SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

from core.constants import (MAX_NAME_LEN, MAX_USERNAME_LEN,
                            MAX_PHONE_NUMBER_LEN, STRANGER)


class Base(DeclarativeBase):
    """The base SQLAlchemy class."""
    type_annotation_map = {
        str: Text()
    }


class User(Base):
    """The User db model."""
    __tablename__ = 'users'

    # User info section:
    id: Mapped[int] = mapped_column(primary_key=True)
    age: Mapped[Optional[int]] = mapped_column(SmallInteger())
    city: Mapped[Optional[str]] = mapped_column(String(MAX_NAME_LEN))
    name: Mapped[Optional[str]] = mapped_column(String(MAX_NAME_LEN))
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(MAX_PHONE_NUMBER_LEN)
    )
    role: Mapped[Optional[str]] = mapped_column(default=STRANGER)
    username: Mapped[Optional[str]] = mapped_column(String(MAX_USERNAME_LEN))

    # Student interests section:
    interests: Mapped[Optional[str]]
    favorite_books: Mapped[Optional[str]]
    favorite_films: Mapped[Optional[str]]
    favorite_games: Mapped[Optional[str]]
    favorite_music: Mapped[Optional[str]]
