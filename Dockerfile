# =================================================================
#    SENTIRIC LLM-LOCAL-SERVICE - CPU & ULTRA-OPTIMIZED (FINAL)
# =================================================================

# --- STAGE 1: Converter ---
# Bu aşama, modeli indirir ve CTranslate2 formatına dönüştürür.
# torch gibi büyük kütüphaneleri içerir ama nihai imajda yer almaz.
FROM python:3.11-slim-bookworm AS converter
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir "ctranslate2[transformers]" "torch" --extra-index-url https://download.pytorch.org/whl/cpu && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Bu komut, modeli indirip /app/model_ct2 klasörüne dönüştürecek.
# Ortam değişkenleri build sırasında sağlanacak.
ARG MODEL_NAME
ARG COMPUTE_TYPE
RUN ct2-transformers-converter --model ${MODEL_NAME} --output_dir model_ct2 --quantization ${COMPUTE_TYPE} --force

# --- STAGE 2: Builder ---
# Bu aşama, sadece runtime için gerekli olan küçük kütüphaneleri derler.
FROM python:3.11-slim-bookworm AS builder
WORKDIR /wheelhouse
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir wheel && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt

# --- STAGE 3: Final Production Image ---
# Bu son imaj, ultra hafif olacak şekilde tasarlanmıştır.
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

# Dönüştürülmüş modeli 'converter' aşamasından kopyala
COPY --from=converter /app/model_ct2 /app/model-cache/converted_model
# Uygulama kodunu kopyala
COPY --chown=appuser:appgroup ./app ./app
# Tokenizer dosyalarını indirmek için cache dizini oluştur
RUN mkdir -p /app/model-cache/hf_tokenizer && chown -R appuser:appgroup /app/model-cache
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:16060/health || exit 1

EXPOSE 16060 16061
CMD ["python", "-m", "app.runner"]