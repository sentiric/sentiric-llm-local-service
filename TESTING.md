# 🧪 Sentiric LLM Local Service - Test Prosedürleri

Bu doküman, servisin başarıyla kurulduğunu ve beklendiği gibi çalıştığını doğrulamak için gereken adımları içerir.

## 1. Ön Koşullar

- Docker ve Docker Compose'un sisteminizde kurulu olması.
- `.env` dosyasının projenin kök dizininde bulunması ve gerekli ortam değişkenlerini içermesi.

## 2. Servisleri Başlatma

Aşağıdaki komut ile CPU tabanlı servisleri başlatın. Bu komut, ilk çalıştırmada model dönüştürme işlemi nedeniyle uzun sürebilir.

```bash
docker compose -f 'docker-compose.cpu.yml' up --build
```

## 3. Doğrulama Adımları

Servisler başarıyla başladıktan sonra aşağıdaki kontrolleri yapın:

### 3.1. Konteyner Durumları

`docker ps` komutunu çalıştırdığınızda, `llm-local-service-cpu` konteynerinin "Up" (Çalışıyor) ve "healthy" (Sağlıklı) durumda olduğunu görmelisiniz. `llm-model-converter` konteyneri ise işini bitirip durmuş olmalıdır.

### 3.2. Sağlık (Health) Endpoint'i

Aşağıdaki `curl` komutunu veya bir tarayıcıyı kullanarak HTTP sağlık kontrolü endpoint'ini sorgulayın:

```bash
curl http://localhost:16060/health
```

**Beklenen Başarılı Yanıt:**
```json
{
  "status": "healthy",
  "model_ready": true,
  "model_name": "microsoft/Phi-3-mini-4k-instruct",
  "device": "cpu"
}
```
Eğer `model_ready` değeri `false` ise, modelin yüklenmesi henüz tamamlanmamış olabilir. Birkaç saniye bekleyip tekrar deneyin.

### 3.3. Metrik (Metrics) Endpoint'i

Prometheus metriklerinin doğru bir şekilde yayınlandığını kontrol edin:

```bash
curl http://localhost:16062/metrics
```

**Beklenen Başarılı Yanıt:**
HTTP istekleri, Python garbage collector vb. ile ilgili bir dizi Prometheus metrik çıktısı görmelisiniz.

### 3.4. gRPC Test İstemcisi

Servisin ana işlevselliği olan token streaming'i test etmek için projenin yerleşik gRPC test istemcisini çalıştırın:

```bash
python grpc_test_client.py "Türkiye'nin başkenti neresidir?"
```

**Beklenen Başarılı Yanıt:**
Terminalde, modelin bu soruya token token ürettiği bir yanıtın akıcı bir şekilde yazıldığını görmelisiniz. Örnek:

```
🔌 Sunucuya bağlanılıyor: localhost:16061
💬 Gönderilen Prompt: 'Türkiye'nin başkenti neresidir?'
--- AI Yanıtı ---
Türkiye'nin başkenti Ankara'dır.
-------------------
✅ Akış başarıyla tamamlandı.
```

Bu adımların tümü başarıyla tamamlandıysa, servis doğru bir şekilde kurulmuş ve çalışıyor demektir.


---
