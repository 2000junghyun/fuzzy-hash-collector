import os
import subprocess
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일에 SEVENZIP_PATH 지정)
load_dotenv()
SEVENZIP_PATH = os.getenv("SEVENZIP_PATH")  # 예: C:\Program Files\7-Zip\7z.exe

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def extract_zip_file(zip_path, extract_dir):
    if not SEVENZIP_PATH:
        raise Exception("SEVENZIP_PATH 환경 변수가 설정되어 있지 않습니다.")
    # 7z x "파일" -o"경로" -aoa -p비번
    cmd = [
        SEVENZIP_PATH, "x", zip_path,
        f"-o{extract_dir}",
        "-aoa",
        "-pinfected"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr.strip())

def extract_zipped_samples(file_type):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SAMPLES_DIR = os.path.join(BASE_DIR, "retrieved_files", "samples")
    ZIP_SAMPLES_DIR = os.path.join(BASE_DIR, "retrieved_files", "zip_samples")

    sample_dir = os.path.join(SAMPLES_DIR, f"{file_type}_samples")
    zip_sample_dir = os.path.join(ZIP_SAMPLES_DIR, f"zipped_{file_type}_samples")

    ensure_dirs(sample_dir, zip_sample_dir)

    count = 0
    for fname in os.listdir(zip_sample_dir):
        if not fname.endswith(".zip"):
            continue
        zip_path = os.path.join(zip_sample_dir, fname)
        try:
            extract_zip_file(zip_path, sample_dir)
            print(f"[Extracted] {fname}")
            count += 1
        except Exception as e:
            print(f"[ERROR] Extract failed for {fname}: {e}")
    print(f"[Summary] {count} files are extracted\n")