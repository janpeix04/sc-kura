# sc-kura
**Kura** was born as my Final Degree Project. Its main goal is to build a privacy-focused storage system platform designed for private networks, such as a home environment.

The project emphasizes full user control over both the system and the stored data, minimizing reliance on third-party services and prioritizing privacy by design.

## Installation/Setup
### Database
From the root of the repository, run the following command:
```bash
docker compose up # Use -d to run in the background
```

### Running the app
To run locally outside docker, just do:
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In another terminal:
```bash
cd frontend
npm run dev
```

To run inside docker, you first need to build the image (and you will need to do so again for any changes done in the code)

```bash
# Work in progress
```

## Alembic
We use **Alembic** for schema migrations. All schema changes must be handled through migrations to keep environment in sync.

### Creating a New Migration
Whenever you modify or add a model, generate a migration:
```bash
cd backend
uv run alembic revision --autogenerate -m "describe your change"
```

> [!WARNING]
> Always review the generated migration (`backend/migrations/versions`) before applying it.

### Applying Migrations
To apply all pending migrations:
```bash
cd backend 
uv run alembic upgrade head
```

To downgrade one revision:
```bash
cd backend 
uv run alembic downgrade -1
```

To downgrade to a specific revision:
```bash
cd backend 
uv run alembic downgrade <revision_id>
```