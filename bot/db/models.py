from sqlalchemy import SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

from core.constants import MAX_NAME_LEN, MAX_USERNAME_LEN


class Base(DeclarativeBase):
    """The base SQLAlchemy class."""
    pass


class User(Base):
    """The User db model."""
    __tablename__ = 'users'

    # User info section:
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(MAX_USERNAME_LEN))
    name: Mapped[str] = mapped_column(String(MAX_NAME_LEN))
    age: Mapped[Optional[int]] = mapped_column(SmallInteger())
    role: Mapped[str] = mapped_column(String())

    # Student interests section:
    interests: Mapped[Optional[str]] = mapped_column(Text())
    favorite_books: Mapped[Optional[str]] = mapped_column(Text())
    favorite_films: Mapped[Optional[str]] = mapped_column(Text())
    favorite_games: Mapped[Optional[str]] = mapped_column(Text())
    favorite_music: Mapped[Optional[str]] = mapped_column(Text())
