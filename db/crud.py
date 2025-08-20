from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from core.exceptions import ToUserError
from core.loggers import get_logger
from db.db_main import engine


logger = get_logger(__name__)

Session = sessionmaker(bind=engine)


# def clear_db():
#     """"""
#     meta = MetaData()

#     with closing(engine.connect()) as con:
#         trans = con.begin()
#         meta.reflect(bind=engine)
#         for table in reversed(meta.sorted_tables):
#             con.execute(table.delete())
#         trans.commit()


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
    try:
        with Session() as session:
            statement = select(obj_class).where(obj_class.id == id)
            obj = session.scalars(statement).one()
        return obj
    except NoResultFound:
        return None


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
