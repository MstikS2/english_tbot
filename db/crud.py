from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import ColumnElement

from core.exceptions import ToUserError
from core.loggers import get_logger
from db.db_main import engine


logger = get_logger(__name__)

Session = sessionmaker(bind=engine)


def exec_with_session(session, func):
    """Executes given func with session() or with session
    depending on whether it is callable."""
    if callable(session):
        with session() as sess:
            result = func(sess)
    else:
        with session:
            result = func(session)
    return result


def create_obj(obj, Session=Session):
    """Creates db obj with given python obj."""
    def orm_func(session, obj=obj):
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

    exec_with_session(Session, orm_func)


def get_all(obj_class, Session=Session):
    """Returns all objects of given class."""
    def orm_func(session, obj_class=obj_class):
        statement = select(obj_class)
        objs = session.scalars(statement).all()
        return objs

    return exec_with_session(Session, orm_func)


def get_obj_where(obj_class, condition: ColumnElement[bool], Session=Session):
    """Returns an object with given condition."""
    def orm_func(session, obj_class=obj_class, condition=condition):
        statement = select(obj_class).where(condition).options(
            selectinload('*')
        )
        obj = session.scalars(statement).one_or_none()
        return obj

    return exec_with_session(Session, orm_func)


def get_obj_list_where(obj_class, condition: ColumnElement[bool],
                       Session=Session):
    """Returns a list of objects with given condition."""
    with Session() as session:
        statement = select(obj_class).where(condition).options(
            selectinload('*')
        )
        objs = session.scalars(statement).all()
    return objs


def object_exists(statement, Session=Session):
    """Checks if object with given statement exists in db."""
    def orm_func(session, statement=statement):
        return session.query(exists().where(statement)).scalar()

    return exec_with_session(Session, orm_func)


def update_obj(obj, Session=Session):
    """Updates db obj with given id."""
    def orm_func(session, obj=obj):
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

    exec_with_session(Session, orm_func)


def delete_by_id(obj_class, id, Session=Session):
    """Deletes db obj by given id."""
    def orm_func(session, obj_class=obj_class, id=id):
        try:
            obj = get_obj_where(obj_class, obj_class.id == id, session)
            child_names = obj.child_names
            if child_names:
                for child_name in child_names:
                    children = getattr(obj, child_name)
                    if children:
                        logger.info(f'Children {children} of {obj} are adding '
                                    'to session')
                        session.add_all(children)
                        logger.info('Child added')
            session.delete(obj)
        except Exception as err:
            logger.error(f'Something went wrong while deleting {obj_class} '
                         f'with id {id}. {err}')
            session.rollback()
            raise ToUserError(
                'Произошла непредвиденная ошибка. '
                'Свяжитесь с администратором или повторите попытку позже'
            )
        else:
            session.commit()
            logger.info(f'Successfully deleted: {obj}')

    exec_with_session(Session, orm_func)
