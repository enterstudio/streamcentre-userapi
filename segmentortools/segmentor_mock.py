import httpretty
import re

def init(config):
    httpretty.register_uri(
        httpretty.POST,
        re.compile(config.start_url.format('(\d+)')),
        content_type='text/json',
        body="ok",
    )

    httpretty.register_uri(
        httpretty.POST,
        re.compile(config.stop_url.format('(\d+)')),
        content_type='text/json',
        body="ok",
    )

    httpretty.register_uri(
        httpretty.GET,
        re.compile(config.status_url.format('(\d+)')),
        content_type='text/json',
        body='{ "status": "ok", "additional field": "pretty value", "just another field": "no woman no cry" }',
    )
