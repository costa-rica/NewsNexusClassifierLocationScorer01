import argparse
from modules.classify_to_csv import classify_location_to_csv
from modules.db_writer import write_scores_to_db_from_csv

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run classification and database write")
    parser.add_argument("--limit", type=int, help="Limit number of articles to classify (default: all)")
    args = parser.parse_args()

    # Step 1: Classify articles and write results to CSV
    print("Starting classification...")
    classify_location_to_csv(limit=args.limit)
    print("Classification complete. Proceeding to write scores to database...")

    # Step 2: Write scores from CSV to database
    write_scores_to_db_from_csv()
    print("Database write complete.")

if __name__ == "__main__":
    main()