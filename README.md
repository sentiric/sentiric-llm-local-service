# 🧠 Sentiric LLM Local Service

**Sentiric LLM Local Service**, yerel donanım üzerinde (on-premise) Büyük Dil Modeli (LLM) çıkarımı sağlayan uzman bir AI motorudur. `CTranslate2` kütüphanesini kullanarak, `Phi-3`, `Llama3` gibi popüler açık kaynaklı modelleri GPU veya CPU üzerinde optimize bir şekilde çalıştırır.

Bu servis, `llm-gateway-service` tarafından, düşük gecikmeli, güvenli veya maliyet-etkin metin üretimi ihtiyaçları için çağrılır.

## 🎯 Temel Sorumluluklar

-   **Yerel Çıkarım:** Harici API'lere ihtiyaç duymadan LLM modellerini çalıştırır.
-   **Yüksek Performans:** `CTranslate2` sayesinde optimize edilmiş ve kuantize edilmiş model çıkarımı.
-   **gRPC Streaming:** Metin yanıtlarını token token üreterek düşük algılanan gecikme sağlar.
-   **Donanım Hızlandırma:** NVIDIA GPU (CUDA) ve CPU için destek.
-   **Dinamik Sağlık Kontrolü:** Modelin yüklenip hazır olup olmadığını bildiren `/health` endpoint'i.

## ⚠️ Model Dönüştürme Süreci (İlk Çalıştırma)

Bu servis ilk kez `docker-compose` ile başlatıldığında, `llm-model-converter` adında bir "init container" çalışır. Bu container'ın tek görevi, `.env` dosyasında belirtilen Hugging Face modelini indirmek ve `CTranslate2` kütüphanesinin kendi aracı olan `ct2-transformers-converter`'ı kullanarak yüksek performanslı bir formata dönüştürmektir.

Bu işlem, modelin CPU için `int8` veya GPU için `float16` gibi formatlara quantize edilmesini (nicemlenmesini) içerir. Bu yaklaşım, önceki yöntemlere göre daha stabildir ve bellek kullanımını daha etkin bir şekilde yönetir.

Yine de, bu işlem modelin büyüklüğüne bağlı olarak **önemli miktarda sistem kaynağı (CPU ve RAM) tüketebilir** ve **uzun sürebilir (10-25+ dakika)**.

### Sistem Gereksinimleri ve Öneriler:
*   **Bellek (RAM):** Dönüştürme işlemi sırasında `microsoft/Phi-3-mini-4k-instruct` gibi bir model için en az 8GB RAM önerilir. Daha büyük modeller için 16GB veya daha fazlası gerekebilir. Yetersiz bellek durumunda işlemin yavaşlaması veya başarısız olması ihtimaline karşı sisteminizde bir **swap alanı** (sanal bellek) bulunması faydalıdır.
*   **Sabır:** İşlem sırasında konteyner loglarında modelin katmanlarının dönüştürüldüğüne dair çıktılar göreceksiniz. Lütfen süreci sonlandırmadan sabırla bekleyin. İşlem tamamlandığında, bu konteyner `exit code 0` ile çıkacak ve ana servis başlayacaktır.

Bu dönüştürme işlemi sadece **ilk çalıştırmada** veya model önbelleği (`model-cache` volume'ü) silindiğinde gerçekleşir. Sonraki başlatmalar çok daha hızlı olacaktır.