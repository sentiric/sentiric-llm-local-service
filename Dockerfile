# STAGE 1: Builder
FROM python:3.11-slim-bookworm AS builder
WORKDIR /wheelhouse
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir wheel && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt

# STAGE 2: Final
FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/model-cache \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
COPY --from=builder /wheelhouse /wheelhouse
RUN pip install --no-cache-dir /wheelhouse/*.whl && rm -rf /wheelhouse /root/.cache/pip
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser
COPY --chown=appuser:appgroup ./app ./app
# DİKKAT: Artık model kopyalama yok, volume'den okunacak
RUN mkdir -p /app/model-cache && chown -R appuser:appgroup /app/model-cache
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:16060/health || exit 1
EXPOSE 16060 16061 16062
CMD ["python", "-m", "app.runner"]