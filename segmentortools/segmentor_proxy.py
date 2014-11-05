# -*- coding: utf-8 -*-
import os
from userapiapp.logger import get_logger
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
import httpretty
import segmentor_mock


class SegmentorProxy(object):
    def __init__(self, config):
        self.use_mock = config['USE_SEGMENTOR_MOCK']
        self.start_url = config['SEGMENTOR_URL_START']
        self.stop_url = config['SEGMENTOR_URL_STOP']
        self.status_url = config['SEGMENTOR_URL_STATUS']


    @httpretty.activate
    def start(self, stream_id, stream_url):
        if self.use_mock: segmentor_mock.init(self)

        full_url = self.start_url.format(stream_id)
        params = { 'url': stream_url }

        try:
            get_logger().info("Start record for stream %d, call [POST] %s", stream_id, full_url)
            response = requests.post(full_url, params=params)
        except Exception:
            get_logger().exception("Cannot call start function for stream %d", stream_id)
            return False
        else:
            if response.status_code == 200:
                return True
            else:
                get_logger().error("Error while calling start function for %d: %s", stream_id, response.text)
                return False


    @httpretty.activate
    def stop(self, stream_id):
        if self.use_mock: segmentor_mock.init(self)

        full_url = self.stop_url.format(stream_id)

        try:
            get_logger().info("Stop record for stream %d, call [POST] %s", stream_id, full_url)
            response = requests.post(full_url)
        except Exception:
            get_logger().exception("Cannot call stop function for stream %d", stream_id)
            return False
        else:
            if response.status_code == 200:
                return True
            else:
                get_logger().error("Error while calling stop function for %d: %s", stream_id, response.text)
                return False


    @httpretty.activate
    def get_status(self, stream_id):
        if self.use_mock: segmentor_mock.init(self)

        full_url = self.status_url.format(stream_id)

        try:
            get_logger().info("Get status of stream %d, call [GET] %s", stream_id, full_url)
            response = requests.get(full_url)
        except Exception:
            get_logger().exception("Cannot call status function for stream %d", stream_id)
            return None
        else:
            if response.status_code == 200:
                return response.json()
            else:
                get_logger().error("Error while calling status function for %d: %s", stream_id, response.text)
                return None
