# bookmarks api

## что умеет

- создать коллекцию
- обновить название коллекции
- удалить коллекцию
- получить список коллекций с пагинацией
- добавить статью в коллекцию
- посмотреть статьи внутри коллекции
- удалить статью из коллекции

## стек

- python 3.12
- fastapi
- pydantic v2
- sqlalchemy 2.x
- postgresql
- alembic
- pytest
- uvicorn

## авторизация

используется простой bearer token без внешних сервисов

все ручки под `/api/v1/collections` требуют заголовок

```http
authorization: bearer dev-secret-token
```

токен задаётся через переменную окружения `AUTH_TOKEN`

## структура проекта

```text
app/
  api/routes/collections.py   # http-ручки
  core/config.py              # настройки
  core/security.py            # проверка bearer token
  core/time.py                # московское время
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
   - `id` as uuid
   - `name`
   - `created_at`
   - `updated_at`

2. `bookmarks`
   - `id` as uuid
   - `title`
   - `url`
   - `created_at`

3. `collection_bookmarks`
   - `collection_id` as uuid
   - `bookmark_id` as uuid
   - `created_at`

### как устроены связи

- `collection` ↔ `bookmark` — связь many-to-many через таблицу `collection_bookmarks`
- один и тот же bookmark можно использовать в нескольких коллекциях
- один и тот же url хранится в `bookmarks` один раз
- все даты и время в ответах сериализуются по московскому часовому поясу

### что защищает от дублей

- `bookmarks.url` помечен как `unique`
- в таблице связи есть `unique(collection_id, bookmark_id)`
- на уровне сервиса есть явная проверка перед добавлением bookmark в коллекцию, чтобы вернуть контролируемую ошибку `409`

## формат ошибок

```json
{
  "error": {
    "code": "collection_not_found",
    "message": "Collection with id=... was not found",
    "details": null
  }
}
```

логика статус-кодов

- `401` — нет заголовка авторизации или неверная схема
- `403` — токен передан, но он неверный
- `404` — сущность не найдена
- `409` — конфликт из-за дубля
- `422` — ошибка валидации входных данных

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

### 3. удалить коллекцию

`DELETE /api/v1/collections/{collection_id}`

ответ

```json
{
  "message": "Collection was deleted"
}
```

### 4. список коллекций

`GET /api/v1/collections?page=1&size=10`

### 5. добавить статью в коллекцию

`POST /api/v1/collections/{collection_id}/bookmarks`

```json
{
  "title": "fastapi docs",
  "url": "https://fastapi.tiangolo.com/"
}
```

### 6. список статей в коллекции

`GET /api/v1/collections/{collection_id}/bookmarks?sort=created_desc`

поддерживаемая сортировка

- `created_asc`
- `created_desc`
- `title_asc`
- `title_desc`
- `url_asc`
- `url_desc`

### 7. удалить статью из коллекции

`DELETE /api/v1/collections/{collection_id}/bookmarks/{bookmark_id}`

ответ

```json
{
  "message": "Bookmark was removed from collection"
}
```

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
cp .env.example .env
```

### 3. при необходимости сменить токен в `.env`

```env
AUTH_TOKEN=dev-secret-token
```

### 4. применить миграции

```bash
make migrate
```

### 5. запустить сервис

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
- токен по умолчанию: `dev-secret-token`

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

в проекте есть тесты на

- обязательную авторизацию
- отклонение неверного токена с `403`
- создание и пагинацию коллекций
- сериализацию времени по москве
- добавление статьи и сортировку
- защиту от дублей
- 404 для несуществующей коллекции
- удаление статьи с сообщением в ответе
- удаление коллекции
- обновление названия коллекции
- единый формат ошибки валидации

## сценарии ручной проверки

1. выполнить `GET /api/v1/collections` без заголовка авторизации и получить `401`
2. выполнить тот же запрос с неверным bearer token и получить `403`
3. создать коллекцию и убедиться, что `id` пришёл как uuid, а `created_at` содержит смещение `+03:00`
4. создать несколько коллекций и проверить пагинацию через `GET /api/v1/collections?page=1&size=2`
5. добавить статью в коллекцию и проверить сортировку через `sort=title_asc` и `sort=created_desc`
6. удалить статью из коллекции и получить json с сообщением об удалении
7. удалить коллекцию и убедиться, что повторный запрос к её статьям возвращает `404`

## негативные сценарии, которые покрыты

- запрос без токена → `401`
- запрос с неверным токеном → `403`
- добавление одной и той же статьи в коллекцию дважды → `409`
- работа с несуществующей коллекцией → `404`
- удаление несуществующей статьи → `404`
- удаление статьи, не привязанной к коллекции → `404`
- невалидный payload с пустым именем, плохим url или неверными query-параметрами → `422`
