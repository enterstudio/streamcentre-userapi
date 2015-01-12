# -*- coding: utf-8 -*-
import os
import requests
from userapiapp.logger import get_logger
import httpretty
import storage_mock


class StorageProxy(object):
    def __init__(self, config):
        self.use_mock = config['USE_STORAGE_MOCK']
        self.info_url = os.path.join(config['STORAGE_URL'], 'info')
        self.clip_url = os.path.join(config['STORAGE_URL'], 'clip/{0}')
        print self.info_url
        print self.clip_url

    @httpretty.activate
    def get_clips_info(self, stream_id, start_stamp, stop_stamp):
        if self.use_mock: storage_mock.init(self)

        params = {
            'stream_id': stream_id,
            'start_time': start_stamp,
            'stop_time': stop_stamp
        }
        get_logger().info("Get meta info %d %s - %s from %s",
            stream_id, start_stamp, stop_stamp, self.info_url)
        response = requests.get(self.info_url, params=params)
        return response.json()


    @httpretty.activate
    def get_clip(self, file_name, clip_id):
        if self.use_mock: storage_mock.init(self)

        clip_url = self.clip_url.format(clip_id)
        get_logger().info("Download clip %d from %s", clip_id, self.clip_url)
        response = requests.get(clip_url, stream=True)

        with open(file_name, 'wb') as f:
            file_size = int(response.headers['content-length'])
            get_logger().info("Download to %s Bytes: %s", file_name, file_size)

            file_size_dl = 0
            for chunk in response.iter_content(chunk_size=8024): 
                if chunk:
                    file_size_dl += len(chunk)
                    f.write(chunk)
                    f.flush()
            get_logger().debug("Clip %s downloaded", file_name)