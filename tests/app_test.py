import os
import unittest
import tempfile
from userapiapp.app import app, init_app
from userapiapp.database import init_db
import json
from userapiapp.database import db_session
from userapiapp.models import Stream
import datetime
import time


class UserapiAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('tests.test_settings')
        init_app(app)
        self.app = app.test_client()
        init_db()


    def tearDown(self):
        pass


    def test_hello(self):
        rv = self.app.get('/hello')
        self.assertIsNotNone(rv.data)


    def test_list(self):
        rv = self.app.get('/streams/')
        janswer = json.loads(rv.data)
        self.assertEqual(len(janswer['result']), 0)

        stream = Stream('test_url', 'test description')
        db_session.add(stream)
        db_session.commit()
        rv = self.app.get('/streams/')
        janswer = json.loads(rv.data)
        self.assertEqual(len(janswer['result']), 1)


    def test_create(self):
        rv = self.app.post('/streams/create')
        self.assertEqual(rv.status_code, 500)

        rv = self.app.post('/streams/create', data={ 'url': 'http://testurl.oi',
                                                     'description': 'test description' })
        self.assertEqual(rv.status_code, 200)
        janswer = json.loads(rv.data)
        self.assertIn('stream_id', janswer)


    def test_start(self):
        stream1 = Stream('test_url_1', 'test_description_1')
        stream2 = Stream('test_url_2', 'test_description_2')
        stream2.start_date = datetime.datetime.now()
        db_session.add(stream1)
        db_session.add(stream2)
        db_session.commit()

        rv = self.app.post('/streams/{0}/start'.format(stream1.id))
        self.assertEqual(rv.status_code, 200)
        stream1 = Stream.query.get(stream1.id)
        self.assertIsNotNone(stream1.start_date)

        rv = self.app.post('/streams/{0}/start'.format(stream2.id))
        self.assertEqual(rv.status_code, 500)
        rv = self.app.post('/streams/{0}/start'.format(stream2.id + 1))
        self.assertEqual(rv.status_code, 404)


    def test_stop(self):
        stream1 = Stream('test_url_1', 'test_description_1')
        stream2 = Stream('test_url_2', 'test_description_2')
        stream3 = Stream('test_url_2', 'test_description_2')
        stream2.start_date = datetime.datetime.now()
        stream3.start_date = datetime.datetime.now()
        stream3.stop_date = datetime.datetime.now()
        db_session.add(stream1)
        db_session.add(stream2)
        db_session.add(stream3)
        db_session.commit()

        rv = self.app.post('/streams/{0}/stop'.format(stream1.id))
        self.assertEqual(rv.status_code, 500)

        rv = self.app.post('/streams/{0}/stop'.format(stream2.id))
        self.assertEqual(rv.status_code, 200)
        stream2 = Stream.query.get(stream2.id)
        self.assertIsNotNone(stream2.stop_date)

        rv = self.app.post('/streams/{0}/stop'.format(stream3.id))
        self.assertEqual(rv.status_code, 500)
        rv = self.app.post('/streams/{0}/stop'.format(stream3.id + 1))
        self.assertEqual(rv.status_code, 404)


    def test_status(self):
        stream = Stream('test_url', 'test_description')
        db_session.add(stream)
        db_session.commit()

        rv = self.app.get('/streams/{0}/status'.format(stream.id + 1))
        self.assertEqual(rv.status_code, 404)

        rv = self.app.get('/streams/{0}/status'.format(stream.id))
        janswer = json.loads(rv.data)
        self.assertEqual(janswer['url'], 'test_url')
        self.assertEqual(janswer['description'], 'test_description')
        self.assertIsNotNone(janswer['create_date'])
        self.assertIsNone(janswer['start_date'])
        self.assertIsNone(janswer['stop_date'])
        self.assertIsNotNone(janswer['status'])

        stream = Stream.query.get(stream.id)
        stream.start_date = datetime.datetime.now()
        stream.stop_date = datetime.datetime.now()
        db_session.commit()

        rv = self.app.get('/streams/{0}/status'.format(stream.id))
        janswer = json.loads(rv.data)
        self.assertIsNotNone(janswer['start_date'])
        self.assertIsNotNone(janswer['stop_date'])


    def test_clip(self):
        stream = Stream('test_url', 'test_description')
        stream.start_date = datetime.datetime.now()
        stream.stop_date = datetime.datetime.now()
        db_session.add(stream)
        db_session.commit()

        rv = self.app.get('/streams/{0}/get_clip'.format(stream.id + 1))
        self.assertEqual(rv.status_code, 404)

        rv = self.app.get('/streams/{0}/get_clip?start=123'.format(stream.id))
        janswer = json.loads(rv.data)
        status = janswer['status']
        self.assertEqual(status, 'pending')
        attempt = 10
        while status != 'done':
            time.sleep(1)
            rv = self.app.get('/streams/{0}/get_clip?start=123'.format(stream.id))
            janswer = json.loads(rv.data)
            status = janswer['status']
            self.assertTrue(attempt, 'Timeout')
            attempt -= 1

        self.assertTrue(janswer['clips'])
        for clip in janswer['clips']:
            self.assertTrue(os.path.exists(clip['link']))
            os.remove(clip['link'])


if __name__ == '__main__':
    unittest.main()