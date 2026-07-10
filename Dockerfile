# Base build
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development build (to run important checks)
FROM base AS development

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN python3 -m ruff check . --extend-select I
RUN python3 -m ruff format --check .
RUN python3 -m pyrefly check --preset all .

# Deployment build
FROM base AS deployment

RUN useradd -m appuser
COPY --from=development --chown=appuser:appuser /app /app

EXPOSE 8000
USER appuser
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
