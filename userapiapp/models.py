# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from userapiapp.database import Base
from userapiapp.help import convert_from_datetime


class Stream(Base):
    __tablename__ = 'stream'
    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    description = Column(String(250))
    create_date = Column(DateTime, nullable=False)
    start_date = Column(DateTime)
    stop_date = Column(DateTime)

    def to_dictionary(self):
        stream_dict = {
                "create_date": convert_from_datetime(self.create_date),
                "description": self.description, 
                "id": self.id, 
                "start_date": convert_from_datetime(self.start_date),
                "stop_date": convert_from_datetime(self.stop_date), 
                "url": self.url
            }
        return stream_dict

    def __init__(self, url, description=None):
        self.url = url
        self.description = description
        self.create_date = datetime.now()

    def __repr__(self):
        return '<Stream %r>' % (self.id)


class ClipRequest(Base):
    __tablename__ = 'clip_request'
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, nullable=False)
    start = Column(DateTime, nullable=False)
    stop = Column(DateTime, nullable=False)
    start_processing_date = Column(DateTime)
    done_date = Column(DateTime)
    links = relationship("ClipLink", backref="request")

    def __init__(self, stream_id, start, stop):
        self.stream_id = stream_id
        self.start = start
        self.stop = stop

    def __repr__(self):
        return '<ClipRequest %r>' % (self.id)


class ClipLink(Base):
    __tablename__ = 'clip_link'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('clip_request.id'))
    file_path = Column(String(250), nullable=False)
    url = Column(String(250), nullable=False)

    def __init__(self, url, path):
        self.url = url
        self.file_path = path

    def __repr__(self):
        return '<ClipLink %r>' % (self.id)