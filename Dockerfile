# CPU için vLLM'in standart bir imajı olmadığından, kendimiz oluşturuyoruz.
FROM python:3.11-slim-bookworm

WORKDIR /app

# Gerekli sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends git curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# CPU için torch'un özel versiyonunu kuruyoruz
RUN sed -i 's/^torch.*/torch --index-url https:\/\/download.pytorch.org\/whl\/cpu/' requirements.txt
# vLLM'i ve diğerlerini kuruyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY ./app ./app

# Diğer proje dosyaları
COPY grpc_test_client.py .
COPY pyproject.toml .

EXPOSE 16060 16061 16062

# --- DÜZELTME: 'python' yerine 'python3' kullanıyoruz ---
CMD ["python3", "-m", "app.runner"]