from utilts.sample_collector import collect_samples
from utilts.extract_zip_handler import extract_zipped_samples
from utilts.fuzzy_hash_handler import process_samples

LIMIT = 5
FILE_TYPE = "elf"

def main():
    # Collect sample files
    collect_samples(limit=LIMIT, file_type=FILE_TYPE)

    # Extract sample files
    extract_zipped_samples(file_type=FILE_TYPE)

    # Calculate fuzzy hash with sample files
    process_samples(file_type=FILE_TYPE)

if __name__ == "__main__":
    main()