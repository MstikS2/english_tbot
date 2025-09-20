from datetime import datetime, timedelta

from pytz import all_timezones
from sqlalchemy import (Column, DateTime, ForeignKey, Interval, MetaData,
                        SmallInteger, String, Table, Text)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, validates)
from typing import Optional

from core.constants import (
    DEFAULT_CITY, DEFAULT_TZ, INT_USER_FIELDS, MAX_CITY_LEN, MAX_USERNAME_LEN,
    MAX_PHONE_NUMBER_LEN, STRANGER, USER_ROLES
)
from core.models import IdModelMixin, NamedModelMixin
from core.exceptions import ToUserError


class Base(DeclarativeBase):
    """The base SQLAlchemy class."""

    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

    type_annotation_map = {
        str: Text(),
        datetime: DateTime()
    }

    @property
    def child_names(self):
        """Returns names of child fields of model.
        Should be redefined in models."""
        pass


class User(NamedModelMixin, Base):
    """The User db model."""

    __tablename__ = 'users'

    # User info section:
    age: Mapped[Optional[int]] = mapped_column(SmallInteger())
    city: Mapped[str] = mapped_column(
        String(MAX_CITY_LEN), server_default=DEFAULT_CITY
    )
    phonenumber: Mapped[Optional[str]] = mapped_column(
        String(MAX_PHONE_NUMBER_LEN)
    )
    role: Mapped[Optional[str]] = mapped_column(default=STRANGER)
    username: Mapped[Optional[str]] = mapped_column(String(MAX_USERNAME_LEN))
    timezone: Mapped[str] = mapped_column(String(), server_default=DEFAULT_TZ)
    price: Mapped[Optional[int]] = mapped_column(SmallInteger())

    # Student interests section:
    interests: Mapped[Optional[str]]
    books: Mapped[Optional[str]]
    films: Mapped[Optional[str]]
    games: Mapped[Optional[str]]
    music: Mapped[Optional[str]]

    # Education section:
    rating: Mapped[int] = mapped_column(SmallInteger(), default=0)
    grade: Mapped[Optional[str]] = mapped_column(String())
    lessons: Mapped[Optional[list['Lesson']]] = relationship(
        back_populates='student'
    )
    points: Mapped[int] = mapped_column(SmallInteger(), default=0)
    # No reminder if null:
    remindtime: Mapped[Optional[timedelta]] = mapped_column(
        Interval(),
        default=timedelta(hours=1)
    )
    book_id: Mapped[Optional[int]] = mapped_column(ForeignKey('books.id'))
    book: Mapped[Optional['Book']] = relationship(back_populates='students')

    @property
    def child_names(self):
        return ('lessons',)

    @validates('role')
    def validate_role(self, key, value):
        """Checks if role is valid."""
        if value not in USER_ROLES:
            raise ToUserError('Роль должна соответствовать одному из этих '
                              f'значений: {USER_ROLES}')
        return value

    @validates('timezone')
    def validate_timezone(self, key, value):
        """Checks if timezone is given in the correct format"""
        if value not in all_timezones:
            raise ToUserError(
                'Часовой пояс должен быть представлен в верном формате. Список'
                ' всех валидных часовых поясов можно посмотреть здесь:\n'
                'https://mljar.com/blog/list-pytz-timezones/'
            )
        return value

    @validates(*INT_USER_FIELDS)
    def validate_ints(self, key, value):
        """Checks if given value is int."""
        try:
            if value is not None:
                return int(value)
        except ValueError:
            raise ToUserError('Пожалуйста, укажите значение числом')


class Category(NamedModelMixin, Base):
    """The db model for category of worlds (like food, buildings etc.)"""

    __tablename__ = 'categories'

    translations: Mapped[list['Translation']] = relationship(
        back_populates='category'
    )
    words: Mapped[list['Word']] = relationship(back_populates='category')

    @property
    def child_names(self):
        return ('translations', 'words')


word_mtm_translation = Table(
    'word_mtm_translation',
    Base.metadata,
    Column('word_id', ForeignKey('words.id'), primary_key=True),
    Column('translation_id', ForeignKey('translations.id'), primary_key=True)
)


word_mtm_unit = Table(
    'word_mtm_unit',
    Base.metadata,
    Column('word_id', ForeignKey('words.id'), primary_key=True),
    Column('unit_id', ForeignKey('units.id'), primary_key=True)
)


class Book(NamedModelMixin, Base):
    """The db model for student's books."""

    __tablename__ = 'books'

    students: Mapped[Optional[list['User']]] = relationship(
        back_populates='book'
    )
    units: Mapped[Optional[list['Unit']]] = relationship(back_populates='book')

    @property
    def child_names(self):
        return ('students', 'units')


class Unit(NamedModelMixin, Base):
    """The db model for student's book's units."""

    __tablename__ = 'units'

    book_id: Mapped[int] = mapped_column(ForeignKey('books.id',
                                                    ondelete='CASCADE'))
    book: Mapped['Book'] = relationship(back_populates='units')
    tasks: Mapped[Optional[list['Task']]] = relationship(back_populates='unit')
    words: Mapped[Optional[list['Word']]] = relationship(
        secondary=word_mtm_unit,
        back_populates='units'
    )

    @property
    def child_names(self):
        return ('tasks',)


class Translation(NamedModelMixin, Base):
    """The db models for Russian translations of English words."""

    __tablename__ = 'translations'

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='translations')
    words: Mapped[list['Word']] = relationship(secondary=word_mtm_translation,
                                               back_populates='translations')


class Word(NamedModelMixin, Base):
    """The db model for English words."""

    __tablename__ = 'words'

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='words')
    tasks: Mapped[list['Task']] = relationship(back_populates='answer')
    translations: Mapped[list['Translation']] = relationship(
        secondary=word_mtm_translation,
        back_populates='words'
    )
    units: Mapped[Optional[list['Unit']]] = relationship(
        secondary=word_mtm_unit,
        back_populates='words'
    )


class Lesson(IdModelMixin, Base):
    """The db model for planned lesson."""

    __tablename__ = 'lessons'

    student_id: Mapped[int] = mapped_column(ForeignKey('users.id',
                                                       ondelete='CASCADE'))
    student: Mapped['User'] = relationship(back_populates='lessons')
    # This field will always contain UTC datetime.
    # User will get both GMT datetime and converted to his timezone datetime
    # according to his city.
    lesson_datetime: Mapped[datetime]
    duration: Mapped[timedelta] = mapped_column(Interval(),
                                                default=timedelta(hours=1))
    price: Mapped[int] = mapped_column(SmallInteger())


class Task(IdModelMixin, Base):
    """The db model for tasks"""

    __tablename__ = 'tasks'

    task: Mapped[str]
    answer_id: Mapped[int] = mapped_column(ForeignKey('words.id',
                                                      ondelete='CASCADE'))
    answer: Mapped['Word'] = relationship(back_populates='tasks')
    unit_id: Mapped[int] = mapped_column(ForeignKey('units.id',
                                                    ondelete='CASCADE'))
    unit: Mapped['Unit'] = relationship(back_populates='tasks')
