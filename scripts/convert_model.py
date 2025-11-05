import os
import sys
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from optimum.intel.openvino import OVModelForCausalLM

# Detaylı loglama için ayarları yap
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logging.getLogger("transformers").setLevel(logging.INFO)
logging.getLogger("optimum").setLevel(logging.INFO)

def main():
    """
    Modeli indirir ve Optimum-Intel (OpenVINO) kullanarak dönüştürür.
    """
    try:
        # 1. Ortam Değişkenlerini STANDART İSİMLERLE Oku
        model_name = os.environ.get("LLM_LOCAL_SERVICE_MODEL_NAME")
        device = os.environ.get("LLM_LOCAL_SERVICE_DEVICE", "cpu")
        # COMPUTE_TYPE, OpenVINO tarafından otomatik yönetildiği için artık
        # bu betikte doğrudan kullanılmıyor, ancak tutarlılık için okunabilir.

        if not model_name:
            logging.error("LLM_LOCAL_SERVICE_MODEL_NAME ortam değişkeni ayarlanmamış.")
            sys.exit(1)

        output_dir = "/models/converted_model"
        os.makedirs(output_dir, exist_ok=True)
        
        logging.info(f"Dönüştürme işlemi başlıyor: {model_name} (Hedef: {device.upper()})")
        
        # 2. Tokenizer'ı yükle
        logging.info("Adım 1/3: Tokenizer yükleniyor...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        # 3. OpenVINO formatına dönüştür
        logging.info("Adım 2/3: Model OpenVINO formatına dönüştürülüyor (BU EN UZUN ADIMDIR, LÜTFEN SABIRLI OLUN)...")
        # Bu sınıf, indirme ve dönüştürme işlemlerini kendi içinde halleder.
        ov_model = OVModelForCausalLM.from_pretrained(
            model_name,
            export=True,
            trust_remote_code=True,
            # Cihazı doğrudan belirtmek, özellikle GPU için önemlidir
            device=device.lower()
        )
        
        # 4. Dönüştürülmüş modeli kaydet
        logging.info("Adım 3/3: Dönüştürülmüş model ve tokenizer diske kaydediliyor...")
        ov_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        logging.info(f"✅ Model başarıyla dönüştürüldü ve '{output_dir}' dizinine kaydedildi.")
        
        # İşlem sonu özeti
        total_size = 0
        file_count = 0
        for root, _, files in os.walk(output_dir):
            file_count += len(files)
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        
        logging.info(f"Özet: {file_count} dosya oluşturuldu. Toplam boyut: {total_size / 1024 / 1024:.2f} MB")

    except Exception:
        logging.error("Dönüştürme işlemi sırasında kritik bir hata oluştu.", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()