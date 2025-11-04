import os
import sys
import structlog

# Bu script, Docker dışında da çalışabilmesi için basit loglama kullanır
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert():
    """
    Ortam değişkenlerinden model adını ve ayarları okuyarak
    CTranslate2 model dönüştürme işlemini yapar.
    """
    model_name = os.environ.get("MODEL_NAME")
    compute_type = os.environ.get("COMPUTE_TYPE", "int8")
    output_dir = "/models/converted_model" # Bu yol volume'e bağlı olacak

    if not model_name:
        logging.error("HATA: MODEL_NAME ortam değişkeni ayarlanmamış.")
        sys.exit(1)

    try:
        from huggingface_hub import snapshot_download
        from ct2_transformers_converter.converter import main as convert_model_main
    except ImportError:
        logging.error("HATA: Gerekli kütüphaneler (transformers, torch, ctranslate2) bulunamadı.")
        sys.exit(1)

    logging.info(f"Orijinal model indiriliyor: {model_name}")
    hf_model_path = snapshot_download(repo_id=model_name, cache_dir="/models/hf_cache")
    logging.info(f"Model indirildi: {hf_model_path}")

    logging.info(f"Model, CTranslate2 formatına dönüştürülüyor ({compute_type})...")
    args = [
        "--model", hf_model_path,
        "--output_dir", output_dir,
        "--quantization", compute_type,
        "--force"
    ]
    convert_model_main(args)
    logging.info(f"✅ Model başarıyla dönüştürüldü ve '{output_dir}' dizinine kaydedildi.")

if __name__ == "__main__":
    convert()