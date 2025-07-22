import os
import csv
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MALWARE_BAZAAR_API_KEY")
API_URL = "https://mb-api.abuse.ch/api/v1/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = os.path.join(BASE_DIR, "retrieved_files", "metadata")
SAMPLES_DIR = os.path.join(BASE_DIR, "retrieved_files", "zip_samples")
FUZZY_HASH_DIR = os.path.join(BASE_DIR, "retrieved_files", "fuzzy_hash")


# Main handler
def collect_samples(limit, file_type):
    hashes = get_sha256_hashes(limit, file_type)
    print(f"[+] {len(hashes)} samples are retrieved from Malware Bazaar")

    new_hashes = filter_sha256_hashes(hashes, file_type)

    downloaded_count = 0
    for sha256 in new_hashes:
        downloaded_count += download_samples(sha256, file_type)
    print(f"[Summary] Downloaded: {downloaded_count}\n")


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
    today_str = datetime.now().strftime("%y%m%d")

    if response.status_code == 200:
        data = response.json()
        if data.get("query_status") == "ok":
            save_metadata_json(file_type, today_str, data)
            return [entry["sha256_hash"] for entry in data.get("data", [])]
        else:
            print(f"[ERROR] API query failed: {data.get('query_status')}")
    else:
        print(f"[ERROR] Status code: {response.status_code}")
    return []


# Save metadata as JSON file
def save_metadata_json(file_type, today_str, data):
    os.makedirs(METADATA_DIR, exist_ok=True)
    metadata_dir = os.path.join(METADATA_DIR, f"{file_type}_metadata")
    metadata_file = os.path.join(metadata_dir, f"{file_type}_sample_metadata_{today_str}.json")

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"[+] Metadata saved to {metadata_file}")


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

    skipped_count = 0
    added_count = 0
    for sha256 in retrieved_hashes:
        if sha256 in existing_hashes:
            print(f"[Skipped] Duplicated sha256 hash exist: {sha256}")
            skipped_count += 1
        else:
            new_hashes.append(sha256)
            added_count += 1
    print(f"[Summary] Added: {added_count}, Skipped: {skipped_count}\n")

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

    download_dir = os.path.join(SAMPLES_DIR, f"zipped_{file_type}_samples")
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, f"{sha256}.zip")

    response = requests.post(API_URL, headers=headers, data=payload)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"[Downloaded] file path: {file_path}")
        return 1
    else:
        print(f"[ERROR] Failed to download {sha256} (Status: {response.status_code})")
        return 0