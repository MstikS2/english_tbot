from datetime import datetime, timedelta

from sqlalchemy import (DateTime, ForeignKey, Interval, SmallInteger, String,
                        Text)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional

from core.constants import (DEFAULT_CITY, DEFAULT_TZ, MAX_CITY_LEN,
                            MAX_USERNAME_LEN, MAX_PHONE_NUMBER_LEN, STRANGER)
from core.models import IdModelMixin, NamedModelMixin


class Base(DeclarativeBase):
    """The base SQLAlchemy class."""

    type_annotation_map = {
        str: Text(),
        datetime: DateTime()
    }


class User(NamedModelMixin, Base):
    """The User db model."""

    __tablename__ = 'users'

    # User info section:
    age: Mapped[Optional[int]] = mapped_column(SmallInteger())
    city: Mapped[str] = mapped_column(
        String(MAX_CITY_LEN), server_default=DEFAULT_CITY
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(MAX_PHONE_NUMBER_LEN)
    )
    role: Mapped[Optional[str]] = mapped_column(default=STRANGER)
    username: Mapped[Optional[str]] = mapped_column(String(MAX_USERNAME_LEN))
    timezone: Mapped[str] = mapped_column(String(), server_default=DEFAULT_TZ)

    # Student interests section:
    interests: Mapped[Optional[str]]
    favorite_books: Mapped[Optional[str]]
    favorite_films: Mapped[Optional[str]]
    favorite_games: Mapped[Optional[str]]
    favorite_music: Mapped[Optional[str]]

    # Education section:
    rating: Mapped[int] = mapped_column(SmallInteger(), default=0)
    grade: Mapped[Optional[str]] = mapped_column(String())
    lessons: Mapped[Optional[list['Lesson']]] = relationship(
        back_populates='student'
    )
    points: Mapped[int] = mapped_column(SmallInteger(), default=0)
    # No reminder if null:
    remind_time: Mapped[Optional[timedelta]] = mapped_column(
        Interval(),
        default=timedelta(hours=1)
    )


class Category(NamedModelMixin, Base):
    """The db model for category of worlds (like food, buildings etc.)"""

    __tablename__ = 'categories'

    translations: Mapped[list['Translation']] = relationship(
        back_populates='category'
    )
    words: Mapped[list['Word']] = relationship(back_populates='category')


class Translation(NamedModelMixin, Base):
    """The db models for Russian translations of English words."""

    __tablename__ = 'translations'

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='translations')


class Word(NamedModelMixin, Base):
    """The db model for English words."""

    __tablename__ = 'words'

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='words')


class Lesson(IdModelMixin, Base):
    """The db model for planned lesson."""

    __tablename__ = 'lessons'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student: Mapped['User'] = relationship(back_populates='lessons')
    # This field will always contain UTC datetime.
    # User will get both GMT datetime and converted to his timezone datetime
    # according to his city.
    lesson_datetime: Mapped[datetime]
    duration: Mapped[timedelta] = mapped_column(Interval(),
                                                default=timedelta(hours=1))


class Task(IdModelMixin, Base):
    """The db model for tasks"""

    __tablename__ = 'tasks'

    task: Mapped[str]
    answer_id: Mapped[int] = mapped_column(ForeignKey('words.id'))
    answer: Mapped['Word'] = relationship(back_populates='tasks')
