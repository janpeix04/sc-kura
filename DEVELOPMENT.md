# **Kura: Development & Contribution Guide**
This document provides instructions for developers who want to **contribute to Kura** or run it locally for development. It includes setup, dependencies, coding standards, and workflow guidelines.

# Prerequisites
To run Kura locally or contribute, ensure you have the following installed:
- [UV](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/)
- Redis
- Nodejs 22+

# Setup & Installation
1. **Clone the repository:**
```bash
git clone https://github.com/janpeix04/sc-kura.git
cd sc-kura
```

2. **Install backend dependencies:**
```bash
cd backend
uv sync
```

3. **Install frontend dependencies:**
```bash
cd frontend
npm ci
```

4. **Configure environment variables** in `backend/.env` as described in the main README.

5. **Start development environment:**
```bash
# Start PostgreSQL database and Adminer
docker compose up postgres adminer -d

# Start backend
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
cd frontend
npm run build:mjml:local
npm run dev

# Start celery
cd backend
source .venv/bin/activate
./celerydev.sh
```

# Workflow & Tools
## Database Migrations
**Alembic** is used for database migrations. Create and apply migrations using inside the `backend` folder:
```bash
uv run alembic revision --autogenerate -m "your message"
```

## OpenAPI Client Generation
**OpenAPI** is used to generate client endpoints from FastAPI. To regenerate clients after changing or adding enpoints, in the `frontend` folder use:
```bash
npm run openapi
```

## Pre-commit Hooks
**Pre-commit** is configured to enforce code quality before commits. Install hooks:
```bash
cd backend
source .venv/bin/activate
cd ..
pre-commit install
```
>[!Note]
>Hooks will automatically run on each commit.

# Development Workflow
1. Fork the repository
2. Create a new branch for your feature over `develop` branch:
```bash
git checkout develop
git checkout -b feat/my-feature
```

3. Make changes, commit, and push:
```bash
git commit -m "feat: describe your feature"
git push origin feat/my-feature
```

4. Open a Pull Request. Ensure all tests pass and pre-commit hooks run cleanly.

# Useful commands
| **Task** | **Command** |
| -------- | ----------- |
| Start database | `docker compose up postgres adminer -d` |
| Stop containers | `docker compose down` |
| Generate secret key | `openssl rand -hex 32` |
| Run backend tests | `uv run pytest` |
| Run frontend checks | `npm run check` |
| Lint frontend code | `npm run lint` |
| Apply database migrations | `uv run alembic upgrade head` |
| Generate a new database migration | `uv run alembic revision --autogenerate -m "your message"`| 
| Generate API clients | `npm run openapi` |

# Contributing
We welcome contributions! Follow the workflow above, write tests for your features, and open issues for bugs or feature requests.

# License
This project follows the same license as the main repository: [MIT License](./LICENSE).