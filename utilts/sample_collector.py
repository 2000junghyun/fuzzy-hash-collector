import os
import csv
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MALWARE_BAZAAR_API_KEY")
API_URL = "https://mb-api.abuse.ch/api/v1/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = os.path.join(BASE_DIR, "retrieved_files", "metadata")
SAMPLES_DIR = os.path.join(BASE_DIR, "retrieved_files", "samples")
FUZZY_HASH_DIR = os.path.join(BASE_DIR, "retrieved_files", "fuzzy_hash")


# Main handler
def collect_samples(limit, file_type):
    hashes = get_sha256_hashes(limit, file_type)
    print(f"[Summary] {len(hashes)} sha256 hashes retrieved\n")

    new_hashes = filter_sha256_hashes(hashes, file_type)
    print(f"[Summary] {len(new_hashes)} new samples to download (filtered from {len(hashes)} total)\n")

    for sha256 in new_hashes:
        download_samples(sha256, file_type)


# Retrieve sha256 hashes
def get_sha256_hashes(limit, file_type):
    headers = {
        "Auth-Key": API_KEY
    }
    payload = {
        "query": "get_file_type",
        "file_type": file_type,
        "limit": limit
    }

    response = requests.post(API_URL, headers=headers, data=payload)
    metadata_file = os.path.join(METADATA_DIR, f"{file_type}_sample_metadata.json")

    if response.status_code == 200:
        data = response.json()

        os.makedirs(METADATA_DIR, exist_ok=True)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[+] Metadata saved to {metadata_file}")

        if data.get("query_status") == "ok":
            return [entry["sha256_hash"] for entry in data.get("data", [])]
        else:
            print(f"[ERROR] API query failed: {data.get('query_status')}")

    else:
        print(f"[ERROR] Status code: {response.status_code}")
    return []


# Filter sha256 hashes
def filter_sha256_hashes(retrieved_hashes, file_type):
    new_hashes = []
    existing_hashes = set()
    fuzzy_hash_csv = os.path.join(FUZZY_HASH_DIR, f"{file_type}_fuzzy_hash.csv")

    if os.path.exists(fuzzy_hash_csv):
        with open(fuzzy_hash_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_hashes.add(row.get("sha256", "").strip())

    for sha256 in retrieved_hashes:
        if sha256 in existing_hashes:
            print(f"[SKIP] Duplicated sha256 hash exist: {sha256}")
        else:
            new_hashes.append(sha256)

    return new_hashes


# Download new samples
def download_samples(sha256, file_type):
    headers = {
        "Auth-Key": API_KEY
    }
    payload = {
        "query": "get_file",
        "sha256_hash": sha256
    }

    download_dir = os.path.join(SAMPLES_DIR, f"{file_type}_samples")
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, f"{sha256}.{file_type}")

    response = requests.post(API_URL, headers=headers, data=payload)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"[Downloaded] file path: {file_path}")
        return
    else:
        print(f"[ERROR] Failed to download {sha256} (Status: {response.status_code})")
        return