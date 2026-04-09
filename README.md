# bookmarks api

## что умеет

- создать коллекцию
- обновить название коллекции
- получить список коллекций с пагинацией
- добавить статью в коллекцию
- посмотреть статьи внутри коллекции с сортировкой
- удалить статью из коллекции

## что внутри

- python 3.12
- fastapi
- pydantic v2
- sqlalchemy 2.x
- postgresql
- alembic
- pytest
- uvicorn

## структура проекта

```text
app/
  api/routes/collections.py   # http-ручки
  core/config.py              # настройки
  db/base.py                  # base + naming convention
  db/models.py                # orm-модели
  db/session.py               # engine + session dependency
  schemas/                    # pydantic-схемы
  services/collections.py     # бизнес-логика
  exceptions.py               # единый формат ошибок
alembic/
  versions/20260409_0001_initial.py
tests/
docker-compose.yml
Dockerfile
Makefile
```

## модель данных

### таблицы

1. `collections`
   - `id`
   - `name`
   - `created_at`
   - `updated_at`

2. `bookmarks`
   - `id`
   - `title`
   - `url`
   - `created_at`

3. `collection_bookmarks`
   - `collection_id`
   - `bookmark_id`
   - `created_at`

### как устроены связи

- `collection` ↔ `bookmark` — связь many-to-many через таблицу `collection_bookmarks`
- один и тот же bookmark можно использовать в нескольких коллекциях
- один и тот же url хранится в `bookmarks` один раз

### что защищает от дублей

- `bookmarks.url` помечен как `unique`
- в таблице связи есть `unique(collection_id, bookmark_id)`
- на уровне сервиса есть явная проверка перед добавлением bookmark в коллекцию, чтобы вернуть контролируемую ошибку `409`, а не необработанный database error

## формат ошибок

```json
{
  "error": {
    "code": "collection_not_found",
    "message": "Collection with id=123 was not found",
    "details": null
  }
}
```

для ошибок валидации

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "name",
        "message": "Value error, Collection name must not be blank",
        "type": "value_error"
      }
    ]
  }
}
```

## api

### 1. создать коллекцию

`POST /api/v1/collections`

```json
{
  "name": "backend reading"
}
```

### 2. обновить название коллекции

`PATCH /api/v1/collections/{collection_id}`

```json
{
  "name": "backend essentials"
}
```

### 3. список коллекций

`GET /api/v1/collections?page=1&size=10`

### 4. добавить статью в коллекцию

`POST /api/v1/collections/{collection_id}/bookmarks`

```json
{
  "title": "fastapi docs",
  "url": "https://fastapi.tiangolo.com/"
}
```

### 5. список статей в коллекции

`GET /api/v1/collections/{collection_id}/bookmarks?sort=created_at`

поддерживаемая сортировка

- `created_at`
- `-created_at`
- `title`
- `-title`
- `url`
- `-url`

### 6. удалить статью из коллекции

`DELETE /api/v1/collections/{collection_id}/bookmarks/{bookmark_id}`

## локальный запуск

### 1. поднять postgresql

например, через docker

```bash
docker compose up db -d
```

### 2. создать и активировать виртуальное окружение

```bash
make install
source .venv/bin/activate
```

### 3. применить миграции

```bash
make migrate
```

### 4. запустить сервис

```bash
make run
```

сервис будет доступен на `http://localhost:8000`, документация — на `http://localhost:8000/docs`

## запуск через docker compose

```bash
make up
```

при старте контейнер api автоматически выполняет

```bash
alembic upgrade head
```

после запуска

- api: `http://localhost:8000`
- swagger: `http://localhost:8000/docs`
- postgresql: `localhost:5432`

остановить

```bash
make down
```

## миграции

применить

```bash
make migrate
```

сгенерировать новую миграцию

```bash
make makemigrations
```

## тесты

```bash
make test
```

## сценарии ручной проверки

1. создать коллекцию `POST /api/v1/collections` и убедиться, что приходит `201` и `id`
2. переименовать коллекцию через `PATCH /api/v1/collections/{id}` и проверить новое имя в ответе
3. создать 3 коллекции и получить `GET /api/v1/collections?page=1&size=2` — должно вернуться 2 элемента и корректные `total/pages`
4. добавить статью в коллекцию и проверить, что она видна в `GET /api/v1/collections/{id}/bookmarks`
5. попробовать добавить тот же url в ту же коллекцию повторно — должен прийти `409`
6. запросить статьи по несуществующей коллекции — должен прийти `404` с кодом `collection_not_found`
7. удалить статью из коллекции и убедиться, что после повторного `GET` список пуст

## негативные сценарии, которые покрыты

- добавление одной и той же статьи в коллекцию дважды → `409`
- работа с несуществующей коллекцией → `404`
- удаление несуществующей статьи → `404`
- удаление статьи, не привязанной к коллекции → `404`
- невалидный payload с пустым именем, плохим url или неверными query-параметрами → `422`
