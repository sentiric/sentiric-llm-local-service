import os
import sys
import logging
from optimum.intel.openvino import OVModelForCausalLM

# Temel loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    """
    Modeli indirir ve Optimum-Intel (OpenVINO) kullanarak dönüştürür.
    """
    try:
        # 1. Ortam Değişkenlerini Oku
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
        model_name = os.environ.get("MODEL_NAME")
        if not model_name:
            logging.error("HATA: MODEL_NAME ortam değişkeni ayarlanmamış.")
            sys.exit(1)

        output_dir = "/models/converted_model"
        
        # 2. Modeli İndir, Dönüştür ve Kaydet (Tek Komut)
        logging.info(f"Model, Optimum-Intel (OpenVINO) formatına dönüştürülüyor: {model_name}")
        
        # Bu sınıf, indirme, dönüştürme ve kaydetme işlemlerini kendi içinde halleder.
        model = OVModelForCausalLM.from_pretrained(
            model_name,
            export=True,
            trust_remote_code=True,
        )
        
        # Dönüştürülmüş modeli belirtilen dizine kaydet
        model.save_pretrained(output_dir)
        
        logging.info(f"✅ Model başarıyla dönüştürüldü ve '{output_dir}' dizinine kaydedildi.")

    except Exception:
        logging.error("Dönüştürme işlemi sırasında kritik bir hata oluştu.", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()