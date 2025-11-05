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

Bu servis ilk kez `docker-compose.cpu.yml` ile başlatıldığında, `llm-model-converter` adında bir "init container" çalışır. Bu container'ın tek görevi, `.env` dosyasında belirtilen Hugging Face modelini indirmek ve `optimum-intel` (OpenVINO) kütüphanesini kullanarak yüksek performanslı bir formata dönüştürmektir.

Bu işlem, modelin büyüklüğüne bağlı olarak **önemli miktarda sistem kaynağı (CPU ve RAM) tüketir** ve **uzun sürebilir (15-30+ dakika)**.

### Sistem Gereksinimleri ve Çözümler:
*   **Bellek (RAM):** Dönüştürme işlemi sırasında `microsoft/Phi-3-mini-4k-instruct` gibi bir model, 8GB'dan fazla RAM'e ihtiyaç duyabilir. Eğer sisteminizde yeterli fiziksel RAM yoksa, işlem `exit code 137` (Out of Memory) hatası ile sonlanabilir.
    *   **Çözüm:** Bu tek seferlik işlem için sisteminize geçici bir **swap alanı** (sanal bellek) eklemeniz şiddetle tavsiye edilir. 16GB RAM'e sahip bir sistemde bile, en az 8-16GB'lık bir swap alanı oluşturmak, işlemin başarıyla tamamlanmasını garanti eder.
*   **Sabır:** İşlem sırasında konteyner loglarında bir süre aktivite görmeyebilirsiniz. Bu normaldir. Lütfen süreci sonlandırmadan sabırla bekleyin. İşlem tamamlandığında, bu konteyner `exit code 0` ile çıkacak ve ana servis başlayacaktır.

Bu dönüştürme işlemi sadece **ilk çalıştırmada** veya model cache'i silindiğinde gerçekleşir. Sonraki başlatmalar çok daha hızlı olacaktır.