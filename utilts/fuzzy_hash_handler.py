import os
import csv
import tlsh
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAMPLES_DIR = os.path.join(BASE_DIR, "retrieved_files", "samples")
FUZZY_HASH_DIR = os.path.join(BASE_DIR, "retrieved_files", "fuzzy_hash")


# Main handler
def process_samples(file_type):
    sample_dir = os.path.join(SAMPLES_DIR, f"{file_type}_samples")
    hash_csv_path = os.path.join(FUZZY_HASH_DIR, f"{file_type}_fuzzy_hash.csv")

    ensure_dirs(sample_dir, FUZZY_HASH_DIR)

    # Fuzzy hash 처리
    process_tlsh_hash(hash_csv_path, sample_dir, file_type)


# Create directories
def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# Process fuzzy hash
def process_tlsh_hash(hash_csv_path, sample_dir, file_type):
    existing_hashes = load_existing_hashes(hash_csv_path)

    # CSV Header
    fieldnames = ['sha256', 'file_name', 'file_type', 'tlsh_hash', 'calculated_time']
    file_exists = os.path.exists(hash_csv_path)
    added = 0
    skipped = 0

    with open(hash_csv_path, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for fname in os.listdir(sample_dir):
            if not fname.endswith(f".{file_type}"):
                continue

            sha256 = fname.replace(f".{file_type}", "")
            if sha256 in existing_hashes:
                print(f"[SKIP] Already hashed: {sha256}")
                skipped += 1
                continue

            file_path = os.path.join(sample_dir, fname)
            fuzzy_hash = calculate_tlsh_hash(file_path)

            if fuzzy_hash:
                writer.writerow({
                    "sha256": sha256,
                    "file_name": fname,
                    "file_type": file_type,
                    "tlsh_hash": fuzzy_hash,
                    "calculated_time": datetime.utcnow().isoformat()
                })
                print(f"[Hashed] file name: {fname}")

                os.remove(file_path)
                added += 1
            else:
                print(f"[WARN] Skipped due to insufficient data: {fname}")
                
                os.remove(file_path)
                skipped += 1

    print(f"[Summary] Added: {added}, Skipped: {skipped}\n")


# Load existing hashes
def load_existing_hashes(csv_path):
    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row['sha256'])
    return existing


# Calculate TLSH hash
def calculate_tlsh_hash(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            if len(data) < 512:
                return None  # TLSH requires minimum data size
            return tlsh.hash(data)
    except Exception as e:
        print(f"[ERROR] Failed to hash {file_path}: {e}")
        return None