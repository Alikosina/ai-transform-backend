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

## Структура

```
app/
  core/config.py       # настройки приложения
  api/routes/          # роуты (health, items)
  schemas/             # Pydantic-схемы
  main.py              # точка входа
```
