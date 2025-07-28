from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import argparse
from modules.article_list_creator import create_article_list
from modules.classify_to_csv import classify_location_to_csv
from modules.db_writer import write_scores_to_db_from_csv

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run classification and database write")
    parser.add_argument("--limit", type=int, help="Limit number of articles to classify (default: all)")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    DB_DIR = os.getenv("PATH_DATABASE")
    DB_NAME = os.getenv("NAME_DB")
    AI_NAME = os.getenv("NAME_AI_ENTITY")
    DB_PATH = os.path.join(DB_DIR, DB_NAME)

    # Connect to DB and check for AI_NAME
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        ai_exists = conn.execute(
            text("SELECT 1 FROM ArtificialIntelligences WHERE name = :name LIMIT 1"),
            {"name": AI_NAME}
        ).fetchone()

    if not ai_exists:
        print(f"Missing '{AI_NAME}' from ArtificialIntelligences table in database.")
        print("--- > Run: python src/standalone/update_ai_entities.py")
        print("Exiting...")
        return

    # Step 1: Create article list
    print("Creating article list...")
    articles_list, processed_ids, existing_results_list = create_article_list(limit=args.limit)

    # Step 2: Classify articles and write results to CSV
    print("Classifying articles...")
    classify_location_to_csv(articles_list, processed_ids, existing_results_list)
    print("Classification complete. Proceeding to write scores to database...")

    # Step 3: Write scores from CSV to database
    write_scores_to_db_from_csv()
    print("Database write complete.")

if __name__ == "__main__":
    main()