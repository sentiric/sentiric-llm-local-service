# =================================================================
#    SENTIRIC LLM-LOCAL-SERVICE - CPU & ULTRA-OPTIMIZED (FINAL v4)
# =================================================================

# --- STAGE 1: Converter ---
# Bu aşama, modeli indirir ve CTranslate2 formatına dönüştürür.
FROM python:3.11-slim-bookworm AS converter
WORKDIR /app

# --- DÜZELTME 1: Tüm bağımlılıkları açıkça kuruyoruz ---
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir \
        "torch" --extra-index-url https://download.pytorch.org/whl/cpu \
        "transformers>=4.38.0" \
        "ctranslate2>=4.0.0" && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG MODEL_NAME
ARG COMPUTE_TYPE

# --- DÜZELTME 2: Script'in tam yolunu bularak python ile çalıştırıyoruz ---
# Bu, tüm kütüphanelerin doğru şekilde bulunmasını garanti eder.
RUN CONVERTER_PATH=$(which ct2-transformers-converter) && \
    python ${CONVERTER_PATH} \
    --model ${MODEL_NAME} \
    --output_dir model_ct2 \
    --quantization ${COMPUTE_TYPE} \
    --force

# --- STAGE 2: Builder ---
FROM python:3.11-slim-bookworm AS builder
WORKDIR /wheelhouse
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir wheel && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt

# --- STAGE 3: Final Production Image ---
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

COPY --from=converter /app/model_ct2 /app/model-cache/converted_model
COPY --chown=appuser:appgroup ./app ./app
RUN mkdir -p /app/model-cache/hf_tokenizer && chown -R appuser:appgroup /app/model-cache
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:16060/health || exit 1

EXPOSE 16060 16061
CMD ["python", "-m", "app.runner"]