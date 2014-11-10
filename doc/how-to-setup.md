# Что нужно поставить
* Python 2.7+
* ffmpeg
* virtualenv

```
$ sudo pip install virtualenv
```

# Как развернуть в дебаге
Cоздать папочку virtualenv.
```
$ virtualenv venv
```

Активировать виртуальное окружение
```
$ . venv/bin/activate
```

Установить все зависимости:
```
$ python setup.py develop
```

Развернуть базу:
```
$ python manage.py initdb
```

Запустить веб-сервер
```
$ python manage.py runserver -p 5000 --threaded
```
запустится веб-сервер на localhost:5000

# Как разворачивать на nginx

Создать папочки
```
/data/www
/data/www/instance
/data/videos
/tmp/videos
```
Проставить им права rwx (чтобы можно было выполнять скрипты, добавлять файлики в папки)

Поставить uwsgi
```
$ pip install uwsgi
```

Настроить nginx (/etc/nginx/sites-available/default):
```
...
server {
	...
	location = /userapi { rewrite ^ /userapi/; }
	location /userapi { try_files $uri @userapi; }
	location @userapi {
	  include uwsgi_params;
	  uwsgi_param SCRIPT_NAME /data/www;
	  uwsgi_modifier1 30;
	  uwsgi_pass unix:/tmp/uwsgi.sock;
	}

	location /videos/ {
		root /data;
	}
	...
}
...
```

Скопировать в /data/www сайтик, добавить конфиг /data/instance/application.cfg:
```
DEBUG = False
DATABASE_URI = 'sqlite:////path_to_database.db'

STORAGE_URL_INFO = 'http://урл_для_получения_метаинформации_из_хранилища'
STORAGE_URL_CLIP = 'http://урл_для_скачивания_фрагментов_видео/'

SEGMENTOR_URL_START = 'http://урл_для_старта_записи_видео/'
SEGMENTOR_URL_STOP = 'http://урл_для_остановки_записи_видео/'
SEGMENTOR_URL_STATUS = 'http://урл_для_получения_статуса_видео/'

TEMP_FOLDER = '/tmp/videos/'
RESULT_CLIPS_FOLDER = '/data/videos/'

DOWNLOAD_LINK_PREFIX = 'http://префикс_ведущий_на_папочку_с_видосиками'

LOG_FILE = 'путь_к_папке_с_логами/название_файла.log'
```


Активизировать окружение, установить зависимости, выйти из акружения
```
$ virtualenv venv
$ . venv/bin/activate
$ python setup.py install
$ deactivate
```

Создать в /data/www файл deploy.ini:
```
[uwsgi]
virtualenv = venv
socket = /tmp/uwsgi.sock
module = userapiapp.app:app
chmod-socket = 666
master
processes = 1
threads = 1
```

Запустить uwsgi
```
uwsgi deploy.ini
```

# Как почистить скачанные видео
```
$ python manage.py clear_old_requests
```
