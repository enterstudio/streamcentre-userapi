import httpretty
import re
import json
import urlparse

def init(config):
    def info_callback(request, uri, headers):
        o = urlparse.urlparse(uri)
        params = urlparse.parse_qs(o.query)
        start_time = float(params['start_time'][0])
        return (200, headers, json.dumps({ 'clips': [{'clip_id': 0, 'start': start_time, 'stop': start_time + 16},
                                         {'clip_id': 1, 'start': start_time + 16, 'stop': start_time + 32},
                                         {'clip_id': 2, 'start': start_time + 32, 'stop': start_time + 48},
                                         {'clip_id': 3, 'start': start_time + 60, 'stop': start_time + 66},
                                         {'clip_id': 4, 'start': start_time + 70, 'stop': start_time + 76},
                                         {'clip_id': 5, 'start': start_time + 76, 'stop': start_time + 112},] }))

    httpretty.register_uri(
        httpretty.GET,
        re.compile(config.info_url.format('(\d+)')),
        content_type='text/json',
        body=info_callback
    )


    def get_clip_callback(method, uri, headers):
        with open('cliptools/sparta.mp4') as f:
            return (200, headers, f.read())


    httpretty.register_uri(
        httpretty.GET,
        re.compile(config.clip_url.format('(\d+)')),
        content_type='video/mp4',
        body=get_clip_callback
    )
