from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer

engine = create_engine('sqlite:///static/db/Bruger.db')
metadata = MetaData()

# Bind metadata to the engine
metadata.bind = engine

Base = declarative_base()

class Users(Base):
    __table__ = Table('users', metadata, autoload_with=engine)

class Answers(Base):
    __table__ = Table('answers', metadata, autoload_with=engine)
