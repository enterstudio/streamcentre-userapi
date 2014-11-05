# -*- coding: utf-8 -*-
TESTING = False
DATABASE_URI = 'sqlite:////tmp/sc_userapi.db'

USE_STORAGE_MOCK = False
STORAGE_URL_INFO = 'http://storage.tv/info'
STORAGE_URL_CLIP = 'http://storage.tv/clip/{0}'

USE_SEGMENTOR_MOCK = False
SEGMENTOR_URL_START = 'http://segmentor.tv/start_rec/{0}'
SEGMENTOR_URL_STOP = 'http://segmentor.tv/stop_rec/{0}'
SEGMENTOR_URL_STATUS = 'http://segmentor.tv/get_state/{0}'

TEMP_FOLDER = '/path_to_temp_folder/'
RESULT_CLIPS_FOLDER = '/path_to_clips_folder/'

DOWNLOAD_LINK_PREFIX = 'http://downloadurl'

FFMPEG_BIN = "ffmpeg"

LOG_FILE = 'userapi.log'
LOG_FORMAT = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'