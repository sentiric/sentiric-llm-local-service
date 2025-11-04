# 🧠 Sentiric LLM Local Service

**Sentiric LLM Local Service**, yerel donanım üzerinde (on-premise) Büyük Dil Modeli (LLM) çıkarımı sağlayan uzman bir AI motorudur. `CTranslate2` kütüphanesini kullanarak, `Phi-3`, `Llama3` gibi popüler açık kaynaklı modelleri GPU veya CPU üzerinde optimize bir şekilde çalıştırır.

Bu servis, `llm-gateway-service` tarafından, düşük gecikmeli, güvenli veya maliyet-etkin metin üretimi ihtiyaçları için çağrılır.

## 🎯 Temel Sorumluluklar

-   **Yerel Çıkarım:** Harici API'lere ihtiyaç duymadan LLM modellerini çalıştırır.
-   **Yüksek Performans:** `CTranslate2` sayesinde optimize edilmiş ve kuantize edilmiş model çıkarımı.
-   **gRPC Streaming:** Metin yanıtlarını token token üreterek düşük algılanan gecikme sağlar.
-   **Donanım Hızlandırma:** NVIDIA GPU (CUDA) ve CPU için destek.
-   **Dinamik Sağlık Kontrolü:** Modelin yüklenip hazır olup olmadığını bildiren `/health` endpoint'i.