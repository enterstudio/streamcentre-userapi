# -*- coding: utf-8 -*-
from flask.ext.script import Manager
from flask import current_app
from userapiapp.app import app, init_app
from userapiapp.database import init_db
from userapiapp.logger import get_logger
from userapiapp.database import db_session
from userapiapp.models import ClipRequest, ClipLink
from datetime import datetime
import os
from cliptools.seamstress import Seamstress
from cliptools.storage_proxy import StorageProxy

init_app(app)
manager = Manager(app)

@manager.command
def hello():
    """
    Print hello
    """
    print "hello"


@manager.command
def initdb():
    """
    Drop and create database
    """
    init_db()


@manager.option('-r', '--request', dest='request_id', default=0)
@manager.option('-t', '--test', dest='test', default=None)
def process_request(request_id, test):
    """
    Start to process clip request. Params: -r <request_id>
    """
    if test:
        print '!!! TEST REQUEST PROCESSING !!!'
        current_app.config.from_object('tests.test_settings')
        init_app(current_app)
        print current_app.config['DATABASE_URI']


    r = ClipRequest.query.get(request_id)
    if r == None:
        get_logger().error("Request %s not found", request_id)
    else:
        r.start_processing_date = datetime.now()
        db_session.commit()
        get_logger().info("Start to process request %s", request_id)

        s = Seamstress(StorageProxy(current_app.config), current_app.config['TEMP_FOLDER'],
            current_app.config['RESULT_CLIPS_FOLDER'], current_app.config['FFMPEG_BIN'])
        output_files = s.compile_clip(r.stream_id, r.start, r.stop, r.id)
        r.done_date = datetime.now()

        for o in output_files:
            link = ClipLink(os.path.join(current_app.config['DOWNLOAD_LINK_PREFIX'], o.split('/')[-1]),
                os.path.join(current_app.config['RESULT_CLIPS_FOLDER'], o))
            r.links.append(link)

        db_session.commit()
        get_logger().info("Finish to process request %s", request_id)


@manager.command
def clear_old_requests():
    """
    Clear all old requests
    """
    requests_count = 0
    files_count = 0
    for request in ClipRequest.query.all():
        for link in request.links:
            if os.path.isfile(link.file_path):
                os.remove(link.file_path)
                files_count += 1
            db_session.delete(link)
        db_session.delete(request)
        requests_count += 1
    count = ClipRequest.query.delete()
    db_session.commit()

    get_logger().info("Old requests cleared. Deleted: %d requests, %d files", requests_count, files_count)
    print "Deleted: {0} requests, {1} files".format(requests_count, files_count)


if __name__ == "__main__":
    manager.run()