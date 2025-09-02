from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker

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


def get_by_id(obj_class, id, Session=Session):
    """Returns obj of obj_class with given id or None if it does not exist."""
    with Session() as session:
        statement = select(obj_class).where(obj_class.id == id).options(
            selectinload('*')
        )
        obj = session.scalars(statement).one_or_none()
    return obj


def get_obj_list_where(obj_class, condition, Session=Session):
    """Returns a list of objects with given condition."""
    with Session() as session:
        statement = select(obj_class).where(condition).options(
            selectinload('*')
        )
        students = session.scalars(statement).all()
    return students


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
            obj = get_by_id(obj_class, id)
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
