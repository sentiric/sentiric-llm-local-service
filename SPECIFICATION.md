# Sentiric LLM Local Service - Teknik Şartname

## 1. Genel Bakış
Bu servis, `llm-gateway-service` için uzman bir AI motoru olarak görev yapar. `CTranslate2` kullanarak yerel LLM çıkarımı sağlar.

## 2. API Arayüzü
- **gRPC:** `sentiric.llm.v1.LLMLocalService` kontratını implemente eder.
  - `rpc LocalGenerateStream(LocalGenerateStreamRequest) returns (stream LocalGenerateStreamResponse)`: Verilen prompt'a karşılık token akışı döndürür.
- **HTTP:** Sadece `/health` endpoint'ini sunar.

## 3. Yapılandırma (Ortam Değişkenleri)
| Değişken | Açıklama | Varsayılan |
| :--- | :--- | :--- |
| `LLM_LOCAL_SERVICE_HTTP_PORT` | HTTP sağlık kontrol portu. | `16060` |
| `LLM_LOCAL_SERVICE_GRPC_PORT` | gRPC servis portu. | `16061` |
| `LLM_LOCAL_SERVICE_MODEL_NAME`| Hugging Face model adı. | `microsoft/Phi-3-mini-4k-instruct`|
| `LLM_LOCAL_SERVICE_DEVICE` | Çalışma cihazı (`cuda`, `cpu`, `auto`). | `auto` |
| `LLM_LOCAL_SERVICE_COMPUTE_TYPE`| Hesaplama hassasiyeti (`float16`, `int8`).| `auto` |