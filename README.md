# sc-kura

## Backend trasnlation (Babel)

1. Extract messages
```bash
uv run pybabel extract -F babel.cfg -o app/i18n/messages.pot .
uv run pybabel update -i app/i18n/messages.pot -d .\app\i18n\locales\ -D messages
```

2. Compile translated messages
```bash
uv run pybabel compile -d .\app\i18n\locales\ -D messages
```

## Run celery
```bash
uv run celery -A app.celery worker -P threads --concurrency=8 --loglevel=info
```