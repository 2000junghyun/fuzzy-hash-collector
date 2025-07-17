from utilts.sample_collector import collect_samples
from utilts.fuzzy_hash_handler import process_samples

LIMIT = 5
FILE_TYPE = "exe"

def main():
    # Collect sample files
    collect_samples(limit=LIMIT, file_type=FILE_TYPE)

    # Calculate fuzzy hash with sample files
    process_samples(file_type=FILE_TYPE)

if __name__ == "__main__":
    main()