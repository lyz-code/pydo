"""
Module to store the models.

Classes:
    Task:
"""

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'
    ulid = Column(String, primary_key=True)
    description = Column(String)
    state = Column(String)


# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# engine = create_engine('sqlite:///' + db_path)
#
# db_path = os.path.expanduser('~/.local/share/pydo/main.db')
# session = sessionmaker()
# session.configure(bind=engine)
