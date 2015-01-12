# API
Все функции возвращают JSON.
*Сейчас по 1-3 пунктам можно и GET и POST запросы делать*

## 0. Список потоков
> [GET] /streams/

### Результат
```
{
  "result": [ ... ]
}
```

## 1. Создание потока
> [POST] /streams/create

### Параметры
* url &mdash; обязательный
* description &mdash; необязательный

### Результат
#### 200 &mdash; Ok
```
{
  "stream_id": 142
}
```

#### 500 &mdash; не передали url
```
{
  "error_message": "URL cannot be empty"
}
```

## 2. Начало записи
> [POST] /streams/\<id>/start

### Результат
#### 200 &mdash; Ok
```
{
  "result": "ok"
}
```

#### 404 &mdash; поток с таким идентификатором не найден
```
{
  "error_message": "Stream not found"
}
```

#### 500 &mdash; поток уже запущен
```
{
  "error_message": "Stream already started"
}
```

#### 500 &mdash; сегментор вернул ошибку
```
{
  "error_message": "Cannot start stream"
}
```

## 3. Остановка записи
> [POST] /streams/\<id>/stop

### Результат
#### 200 &mdash; Ok
```
{
  "result": "ok"
}
```

#### 404 &mdash; поток с таким идентификатором не найден
```
{
  "error_message": "Stream not found"
}
```

#### 500 &mdash; поток не запущен или уже остановлен
```
{
  "error_message": "Stream not started"
}
```

#### 500 &mdash; сегментор вернул ошибку
```
{
  "error_message": "Cannot stop stream"
}
```

## 4. Запрос статуса
> [GET] /streams/\<id>/status

### Результат
#### 200 &mdash; Ok
```
{
  "create_date": [unix-time], 
  "description": "asdsaccascasdasd", 
  "id": 1, 
  "start_date": [unix-time], 
  "stop_date": [unix-time], 
  "url": "asdasdasdadsadsaddscasc"
}
```

#### 404 &mdash; поток с таким идентификатором не найден
```
{
  "error_message": "Stream not found"
}
```

#### 500 &mdash; сегментор вернул ошибку
```
{
  "error_message": "Cannot get stream status"
}
```

## 5. Получение фрагмента видео
> [GET] /streams/\<id>/get_clip

### Параметры
* start &mdash; обязательный ([POSIX timestamp](http://en.wikipedia.org/wiki/Unix_time))
* stop &mdash; необязательный ([POSIX timestamp](http://en.wikipedia.org/wiki/Unix_time))

### Результат
#### 200 &mdash; Ok. Возможные статусы: "pending", "processing", "done". Ссылки появляются только в финальном состоянии
```
{
  "status": "done",
  "clips": [
    {
      "link": "https://clipstore.loc/asdasdww12"
    },
    {
      "link": "https://clipstore.loc/asasdda32sdww12"
    },
    {
      "link": "https://clipstore.loc/asddsa11sdww12"
    }
  ]
}
```

#### 404 &mdash; поток с таким идентификатором не найден
```
{
  "error_message": "Stream not found"
}

```
#### 500 &mdash; поток не запущен
```
{
  "error_message": "Stream not started"
}
```
