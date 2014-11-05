from logging.handlers import TimedRotatingFileHandler
import logging

_logger = None


def get_logger():
    return _logger


def set_logger_params(app):
    global _logger
    _logger = app.logger
    handler = TimedRotatingFileHandler(app.config['LOG_FILE'], when='D', interval=1)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    _logger.addHandler(handler)