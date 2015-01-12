# -*- coding: utf-8 -*-
TESTING = False
DATABASE_URI = 'sqlite:////tmp/sc_userapi.db'

USE_STORAGE_MOCK = False
STORAGE_URL = 'http://storage.tv'

USE_SEGMENTOR_MOCK = False
SEGMENTOR_URL = 'http://segmentor.tv'

TEMP_FOLDER = '/path_to_temp_folder/'
RESULT_CLIPS_FOLDER = '/path_to_clips_folder/'

DOWNLOAD_LINK_PREFIX = 'http://downloadurl'

FFMPEG_BIN = "ffmpeg"

LOG_FILE = 'userapi.log'
LOG_FORMAT = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'