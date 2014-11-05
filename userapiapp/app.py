# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, current_app
from datetime import datetime
from time import strptime
from userapiapp.help import convert_from_datetime, convert_to_datetime
from userapiapp.logger import get_logger, set_logger_params
from segmentortools.segmentor_proxy import SegmentorProxy
from userapiapp.database import db_session, init_engine
from userapiapp.models import Stream, ClipRequest, ClipLink
from subprocess import Popen
from crossdomain_decorator import crossdomain


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('userapiapp.default_settings')
app.config.from_pyfile('application.cfg', silent=True)

segmentor_proxy = None

def init_app(app):
    set_logger_params(app)
    init_engine(app.config['DATABASE_URI'], convert_unicode=True)
    global segmentor_proxy
    segmentor_proxy = SegmentorProxy(app.config)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/hello')
def hello():
    get_logger().info('Hello!')
    return 'Hello! I\'m UserAPI application!'


@app.route('/streams/create', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type'])
def create():
    if request.json:
        url = request.json.get('url')
        description = request.json.get('description')
    else:
        url = request.form.get('url')
        description = request.form.get('description')

    if not url:
        return jsonify(error_message='URL cannot be empty'), 500
    else:
        stream = Stream(url, description)
        db_session.add(stream)
        db_session.commit()

        get_logger().info("Stream %d (url: %s , description: %s) created", stream.id, stream.url, stream.description)

        return jsonify(stream_id=stream.id)


@app.route('/streams/')
@crossdomain(origin='*')
def list():
    streamsList = Stream.query.all()
    streamsDictionary = [stream.to_dictionary() for stream in streamsList]
    return jsonify(result=streamsDictionary)


@app.route('/streams/<int:stream_id>/start', methods=['POST'])
@crossdomain(origin='*')
def start(stream_id):
    stream = Stream.query.get(stream_id)
    if stream:
        if stream.start_date:
            return jsonify(error_message='Stream already started'), 500
        else:
            if segmentor_proxy.start(stream.id, stream.url):
                stream.start_date = datetime.now()
                db_session.commit()
                
                get_logger().info("Stream %d started", stream.id)
                return jsonify(result='ok')
            else:
                get_logger().error("Cannot start stream %d", stream.id)
                return jsonify(error_message='Cannot start stream'), 500
    else:
        return jsonify(error_message='Stream not found'), 404


@app.route('/streams/<int:stream_id>/stop', methods=['POST'])
@crossdomain(origin='*')
def stop(stream_id):
    stream = Stream.query.get(stream_id)
    if stream:
        if not stream.start_date:
            return jsonify(error_message='Stream not started'), 500
        elif stream.stop_date:
            return jsonify(error_message='Stream already stopped'), 500
        else:
            if segmentor_proxy.stop(stream.id):
                stream.stop_date = datetime.now()
                db_session.commit()

                get_logger().info("Stream %d stopped", stream.id)

                return jsonify(result='ok')
            else:
                get_logger().error("Cannot stop stream %d", stream.id)
                return jsonify(error_message='Cannot stop stream'), 500
    else:
        return jsonify(error_message='Stream not found'), 404


@app.route('/streams/<int:stream_id>/status')
@crossdomain(origin='*')
def status(stream_id):
    stream = Stream.query.get(stream_id)
    if stream:
        status = segmentor_proxy.get_status(stream.id)
        info = {
            'id': stream.id,
            'url': stream.url,
            'description': stream.description,
            'create_date': convert_from_datetime(stream.create_date),
            'start_date': convert_from_datetime(stream.start_date),
            'stop_date': convert_from_datetime(stream.stop_date),
            'status': status
        }
        return jsonify(**info)
    else:
        return jsonify(error_message='Stream not found'), 404


@app.route('/streams/<int:stream_id>/get_clip')
@crossdomain(origin='*')
def get_clip(stream_id):
    stream = Stream.query.get(stream_id)
    if stream:
        if not stream.start_date:
            return jsonify(error_message='Stream not started'), 500
        else:
            if request.method == 'POST':
                start = request.form.get('start')
                stop = request.form.get('stop')
            else:
                start = request.args.get('start')
                stop = request.args.get('stop')

            start = convert_to_datetime(int(start)) if start else stream.start_date

            if stop:
                stop = convert_to_datetime(int(stop))
            else:
                if stream.stop_date != None:
                    stop = stream.stop_date
                else:
                    stop = datetime.now()

            clip_request = ClipRequest.query.filter(ClipRequest.stream_id==stream_id,
                ClipRequest.start==start, ClipRequest.stop==stop).first()

            if not clip_request:
                clip_request = ClipRequest(stream_id, start, stop)
                db_session.add(clip_request)
                db_session.commit()

                get_logger().info("Clip request %d for stream %d (%s - %s) created", clip_request.id,
                    stream_id, start, stop)

                pop_params = ['python', 'manage.py', 'process_request', '-r', str(clip_request.id)]
                if current_app.config['TESTING']: pop_params += ['-t', 'True']
                pop = Popen(pop_params)

            if not clip_request.start_processing_date:
                result = {'status': 'pending'}
            elif not clip_request.done_date:
                result = {'status': 'processing'}
            else:
                clips = [{ 'link': link.url } for link in clip_request.links]
                result = {'status': 'done', 'clips': clips}

            return jsonify(**result)
    else:
        return jsonify(error_message='Stream not found'), 404