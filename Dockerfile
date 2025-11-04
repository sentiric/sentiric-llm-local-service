# STAGE 1: Builder
FROM python:3.11-slim-bookworm AS builder
WORKDIR /wheelhouse
RUN pip install --no-cache-dir wheel
COPY pyproject.toml .
RUN pip wheel --no-cache-dir -r requirements.txt_from_toml

# STAGE 2: Final Production Image
FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv

COPY --from=builder /wheelhouse /wheelhouse
RUN pip install --no-cache-dir /wheelhouse/*.whl && rm -rf /wheelhouse

RUN adduser --system --group appuser
COPY --chown=appuser:appuser ./app ./app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=15m --retries=3 \
    CMD curl -f http://localhost:16060/health || exit 1

EXPOSE 16060 16061
CMD ["python", "-m", "app.runner"]