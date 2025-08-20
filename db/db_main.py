from sqlalchemy import create_engine

from core.loggers import get_logger
from db.models import Base


logger = get_logger('sqlalchemy')

engine = create_engine('sqlite:///db/Database.db')


def create_db():
    """Create the db with all related tables."""
    Base.metadata.create_all(bind=engine)
