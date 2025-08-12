# Fuzzy Hash Collector

## Overview

This project automates **malware sample collection, archive extraction, and fuzzy hash (TLSH) calculation**, enabling continuous accumulation of a malware database.

It fetches the latest samples of a specified file type (EXE/ELF) from the MalwareBazaar API, extracts password-protected ZIP files, calculates TLSH hashes, and appends them to a CSV file.

<br><br>

Designed to reflect a real-world malware analysis and research environment, it operates in the following stages:

- **Sample Collection**: Download the latest malware samples via API
- **Archive Extraction**: Bulk extraction using the 7-Zip CLI
- **Fuzzy Hash Calculation**: TLSH-based hash generation and CSV storage
- **Duplicate Prevention**: Skip already processed samples for efficient management

## Tech Stack

- **Language**: Python 3.9
- **Libraries**: requests, TLSH, python-dotenv
- **External Tools**: 7-Zip CLI
- **Environment**: Local machine or analysis server

## Directory Structure

```
.
├── retrieved_files
│   ├── fuzzy_hash/                # TLSH hash CSV storage
│   ├── metadata/                   # Sample metadata (JSON)
│   ├── samples/                    # Extracted samples
│   └── zip_samples/                # Downloaded ZIP files
│
├── utilts
│   ├── extract_zip_handler.py      # Archive extraction module
│   ├── fuzzy_hash_handler.py       # TLSH calculation module
│   └── sample_collector.py         # Sample collection module
│
├── .env                            # API key and 7-Zip path configuration
├── main.py                         # Pipeline entry point
└── README.md
```

## How It Works

### 1. Sample Collection (`sample_collector.py`)

- Retrieves the latest SHA256 list for the specified file type from the MalwareBazaar API
- Filters out hashes already present in the CSV and downloads the remaining samples as ZIP archives
- Stores associated metadata in JSON format

### 2. Archive Extraction (`extract_zip_handler.py`)

- Uses the `SEVENZIP_PATH` in `.env` to call the 7-Zip CLI for extraction
- Automatically applies the password `infected`
- Deletes the original ZIP files after extraction

### 3. Fuzzy Hash Calculation (`fuzzy_hash_handler.py`)

- Calculates TLSH hashes for the extracted files
- Appends results to `retrieved_files/fuzzy_hash/<type>_fuzzy_hash.csv`
- Skips already existing hashes
- Deletes original sample files after processing

### 4. Full Pipeline Execution (`main.py`)

- Executes the entire process—sample collection → extraction → hash calculation—in sequence

## How to Run Locally

### 1. Configure Environment Variables

Example `.env` file:

```
MALWARE_BAZAAR_API_KEY=your_api_key
SEVENZIP_PATH=C:\Program Files\7-Zip\7z.exe
```

### 2. Run

```bash
python main.py
```

- Adjust `LIMIT` (download count) and `FILE_TYPE` ("exe" / "elf") in `main.py` as needed

## Features / Main Logic

- **Automated Sample Pipeline**
    - Collect, extract, and hash in a single run
- **TLSH-based Fuzzy Hashing**
    - Enables similarity detection for malware variants
- **Duplicate Prevention**
    - Skips existing hashes to save storage and processing time
- **Metadata Archiving**
    - Stores JSON metadata by date for historical tracking

## Future

- Add similarity-based automatic classification using TLSH
- Integrate with S3 or databases for centralized storage
- Implement automated scheduling (Cron, Airflow)
- Use multithreading/parallel processing for large-scale handling

## Motivation / Impact

- **Improved Research Efficiency**: Automates large-scale malware sample management
- **Supports Similarity Analysis**: Facilitates variant detection via TLSH
- **Real-world Workflow Simulation**: Replaces repetitive manual extraction and hashing with code