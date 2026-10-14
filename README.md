# transform-backend

Базовый бекенд на FastAPI.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API будет доступно на http://127.0.0.1:8000, интерактивная документация — на http://127.0.0.1:8000/docs.

## Запуск в Docker

```bash
cp .env.example .env
docker compose up --build -d
```

API будет доступно на http://127.0.0.1:3001, документация — на http://127.0.0.1:3001/docs.

Вместе с бекендом поднимается PostgreSQL (сервис `db`). Перед первым запуском задайте в `.env`
`POSTGRES_PASSWORD` (`openssl rand -hex 32`) и тот же пароль в `DATABASE_URL`.
Миграции (Alembic) применяются автоматически при старте контейнера бекенда.

Новая миграция после изменения моделей:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "описание"
```

## Структура

```
app/
  core/config.py       # настройки приложения
  core/database.py     # подключение к PostgreSQL (SQLAlchemy async)
  api/routes/          # роуты (health, items, llm, mock, portfolio)
  models/              # SQLAlchemy-модели
  schemas/             # Pydantic-схемы
migrations/            # миграции Alembic
  main.py              # точка входа
```
