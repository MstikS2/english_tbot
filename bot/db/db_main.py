from sqlalchemy import create_engine

from bot.db.models import Base


engine = create_engine('sqlite:///bot/db/Database.db', echo=True)


def create_db():
    """Create the db with all related tables."""
    Base.metadata.create_all(bind=engine)
