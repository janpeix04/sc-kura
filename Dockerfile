# syntax=docker/dockerfile:1

# ==========================
# Stage 1: Frontend builder
# ==========================
FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /workspace

RUN mkdir -p frontend app/email_templates/src app/email_templates/build
COPY backend/app/email_templates/src ./app/email_templates/src
COPY frontend/package*.json ./frontend/

WORKDIR /workspace/frontend

RUN npm ci
COPY frontend/ .
RUN npm run build

# ==========================
# Stage 2: Backend setup
# ==========================
ARG PYTHON_VERSION=3.12
ENV PYTHON_VERSION=${PYTHON_VERSION}
ENV LANG="C.UTF-8" LC_ALL="C.UTF-8"
WORKDIR /workspace

# System deps
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates curl python3-pip nodejs g++ make \
    && rm -rf /var/lib/apt/lists/*

# Install node (22)
RUN apt-get remove -y nodejs npm || true \
    && rm -f /usr/bin/node /usr/bin/npm /usr/local/bin/node /usr/local/bin/npm || true \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs

# Install uv
RUN pip install --break-system-packages -U pip uv

# Backend deps
COPY backend/uv.lock backend/pyproject.toml ./

# Create and sync the environment
RUN uv venv --python ${PYTHON_VERSION} \
    && uv sync --locked --no-dev

# Backend code
COPY backend/ .

# Entrypoint
WORKDIR /workspace
EXPOSE 8000 3000
COPY supervisor.py /supervisor.py
CMD ["uv", "run", "--no-dev", "python", "/supervisor.py"]
