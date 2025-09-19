from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import ColumnElement

from core.exceptions import ToUserError
from core.loggers import get_logger
from db.db_main import engine


logger = get_logger(__name__)

Session = sessionmaker(bind=engine)


def create_obj(obj, Session=Session):
    """Creates db obj with given python obj."""
    with Session() as session:
        try:
            session.add(obj)
        except Exception as err:
            logger.error(f'Something went wrong while creating {obj}. {err}')
            session.rollback()
            raise ToUserError(
                'Произошла непредвиденная ошибка. '
                'Свяжитесь с администратором или повторите попытку позже'
            )
        else:
            session.commit()
            logger.info(f'Successfully created: {obj}')


def get_all(obj_class, Session=Session):
    """Returns all objects of given class."""
    with Session() as session:
        statement = select(obj_class)
        objs = session.scalars(statement).all()
    return objs


def get_obj_where(obj_class, condition: ColumnElement[bool], Session=Session):
    """Returns an object with given condition."""
    with Session() as session:
        statement = select(obj_class).where(condition).options(
            selectinload('*')
        )
        obj = session.scalars(statement).one_or_none()
    return obj


def get_obj_list_where(obj_class, condition: ColumnElement[bool],
                       Session=Session):
    """Returns a list of objects with given condition."""
    with Session() as session:
        statement = select(obj_class).where(condition).options(
            selectinload('*')
        )
        objs = session.scalars(statement).all()
    return objs


def object_exists(statement):
    """Checks if object with given statement exists in db."""
    with Session() as session:
        return session.query(exists().where(statement)).scalar()


def update_obj(obj, Session=Session):
    """Updates db obj with given id."""
    with Session() as session:
        try:
            session.merge(obj)
        except Exception as err:
            logger.error(f'Something went wrong while updating {obj}. {err}')
            session.rollback()
            raise ToUserError(
                'Произошла непредвиденная ошибка. '
                'Свяжитесь с администратором или повторите попытку позже'
            )
        else:
            session.commit()
            logger.info(f'Successfully updated: {obj}')


def delete_by_id(obj_class, id, Session=Session):
    """Deletes db obj by given id."""
    with Session() as session:
        try:
            obj = get_obj_where(obj_class, obj_class.id == id)
            session.delete(obj)
        except Exception as err:
            logger.error(f'Something went wrong while deleting {obj}. {err}')
            session.rollback()
            raise ToUserError(
                'Произошла непредвиденная ошибка. '
                'Свяжитесь с администратором или повторите попытку позже'
            )
        else:
            session.commit()
            logger.info(f'Successfully deleted: {obj}')
