import os
import sys
import logging
import subprocess
from pathlib import Path

# Temel loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    """
    Bir Hugging Face modelini, CTranslate2 formatına dönüştürür.
    Bu script, ct2-transformers-converter aracını sarmalar ve yapılandırır.
    """
    try:
        # 1. Ortam Değişkenlerini Oku
        model_name = os.environ.get("LLM_LOCAL_SERVICE_MODEL_NAME")
        compute_type = os.environ.get("LLM_LOCAL_SERVICE_COMPUTE_TYPE", "auto")
        
        if not model_name:
            logging.error("LLM_LOCAL_SERVICE_MODEL_NAME ortam değişkeni ayarlanmamış.")
            sys.exit(1)

        output_dir = "/models/converted_model"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logging.info(f"Model dönüştürme işlemi başlatılıyor...")
        logging.info(f"  - Model Adı: {model_name}")
        logging.info(f"  - Hesaplama Tipi (Quantization): {compute_type}")
        logging.info(f"  - Çıktı Dizini: {output_dir}")

        # 2. CTranslate2 Dönüştürücü Komutunu Oluştur
        # --- DÜZELTME: Argümanları en uyumlu formatta yeniden düzenliyoruz ---
        command = [
            "ct2-transformers-converter",
            "--model", model_name,
            "--output_dir", output_dir,
            "--force"
        ]
        
        # Bu argümanlar her zaman gerekli
        command.extend(["--copy_files", "tokenizer_config.json", "special_tokens_map.json", "tokenizer.json"])
        command.append("--trust_remote_code")

        if compute_type != "auto":
            command.extend(["--quantization", compute_type])

        # 3. Dönüştürme İşlemini Çalıştır
        logging.info(f"Çalıştırılacak komut: {' '.join(command)}")
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')

        for line in iter(process.stdout.readline, ''):
            logging.info(line.strip())
        
        process.wait()

        if process.returncode != 0:
            logging.error(f"Model dönüştürme işlemi başarısız oldu! (Exit Code: {process.returncode})")
            sys.exit(process.returncode)

        logging.info(f"✅ Model başarıyla dönüştürüldü ve '{output_dir}' dizinine kaydedildi.")

    except Exception:
        logging.error("Dönüştürme betiğinde kritik bir hata oluştu.", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()