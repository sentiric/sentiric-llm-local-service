import os
import sys
import logging
import subprocess

# Temel loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def run_command(command):
    """Bir komutu çalıştırır ve çıktısını canlı olarak loglar."""
    logging.info(f"Komut çalıştırılıyor: {' '.join(command)}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8'
    )
    for line in process.stdout:
        print(line, end='', flush=True)
    process.wait()
    print() 
    if process.returncode != 0:
        logging.error(f"Komut başarısız oldu! Çıkış kodu: {process.returncode}")
        sys.exit(process.returncode)

def main():
    """
    Modeli indirir, dönüştürür ve temizlik yapar.
    """
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

    model_name = os.environ.get("MODEL_NAME")
    compute_type_input = os.environ.get("COMPUTE_TYPE", "auto")
    device = os.environ.get("DEVICE", "cpu")
    
    # "auto" değerini CTranslate2'nin anlayacağı formata çevir
    if compute_type_input == "auto":
        if device == "cuda":
            compute_type = "float16"
            logging.info(f"'{compute_type_input}' compute type detected for CUDA device, setting quantization to '{compute_type}'.")
        else:
            compute_type = "int8"
            logging.info(f"'{compute_type_input}' compute type detected for CPU device, setting quantization to '{compute_type}'.")
    else:
        compute_type = compute_type_input

    output_dir = "/models/converted_model"
    hf_cache_dir = "/models/hf_cache"

    if not model_name:
        logging.error("HATA: MODEL_NAME ortam değişkeni ayarlanmamış.")
        sys.exit(1)

    # 1. Gerekli kütüphaneleri kur
    run_command([
        "pip", "install", "--no-cache-dir",
        "torch", "--extra-index-url", "https://download.pytorch.org/whl/cpu",
        "ctranslate2[transformers]>=4.0.0",
        "huggingface-hub>=0.20.0"
    ])
    
    # 2. Modeli indir (Python içinden)
    from huggingface_hub import snapshot_download
    logging.info(f"Orijinal model indiriliyor: {model_name}")
    hf_model_path = snapshot_download(repo_id=model_name, cache_dir=hf_cache_dir)
    logging.info(f"Model indirildi: {hf_model_path}")

    # 3. Modeli dönüştür (Komut satırı aracını çağırarak)
    run_command([
        "ct2-transformers-converter",
        "--model", hf_model_path,
        "--output_dir", output_dir,
        "--quantization", compute_type,
        "--force"
    ])
    
    logging.info(f"✅ Model başarıyla dönüştürüldü ve '{output_dir}' dizinine kaydedildi.")

if __name__ == "__main__":
    main()