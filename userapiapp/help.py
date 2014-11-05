from datetime import datetime
import time


def convert_to_datetime(stamp):
    return datetime.fromtimestamp(int(stamp)) if stamp else None
        

def convert_from_datetime(dt):
    return time.mktime(dt.timetuple()) if dt else None
        