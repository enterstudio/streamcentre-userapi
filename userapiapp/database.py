# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, create_session
from sqlalchemy.ext.declarative import declarative_base
from userapiapp.logger import get_logger

engine = None
db_session = scoped_session(lambda: create_session(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs)
    return engine

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import userapiapp.models
    Base.metadata.drop_all(bind=engine)
    get_logger().info('Database dropped')
    Base.metadata.create_all(bind=engine)
    get_logger().info('Database created')