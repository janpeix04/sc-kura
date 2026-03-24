# sc-kura

## Babel i18n
1. extract messages:
```bash
uv run pybabel extract -F babel.cfg -o app/i18n/messages.pot .
uv run pybabel update -i app/i18n/messages.pot -d .\app\i18n\locales\ -D messages
```

2. Compile messages:
```bash
uv run pybabel compile -d .\app\i18n\locales\ -D messages
```