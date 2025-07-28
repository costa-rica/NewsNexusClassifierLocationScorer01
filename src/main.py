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
    # DB_DIR = os.getenv("PATH_DATABASE")
    # DB_NAME = os.getenv("NAME_DB")
    AI_NAME = os.getenv("NAME_AI_ENTITY")
    # DB_PATH = os.path.join(DB_DIR, DB_NAME)


    entity_who_categorized_article_id = get_entity_who_categorized_article_id()
    print(f"EntityWhoCategorizedArticle ID: {entity_who_categorized_article_id}")

    if not entity_who_categorized_article_id:
        print(f"Missing '{AI_NAME}' from ArtificialIntelligences table in database.")
        print("--- > Run: python src/standalone/update_ai_entities.py")
        print("Exiting...")
        return

    # Step 1: Create article list
    print("Creating article list...")
    articles_list, processed_ids, existing_results_list = create_article_list(entity_who_categorized_article_id,limit=args.limit)

    # Step 2: Classify articles and write results to CSV
    print("Classifying articles...")
    df_length = classify_location_to_csv(articles_list, processed_ids, existing_results_list)
    print("Classification complete. Proceeding to write scores to database...")

    # Step 3: Write scores from CSV to database
    if df_length > 0:
        write_scores_to_db_from_csv()
        print("Database write complete.")
    else:
        print("No data to write to the database.")



def get_entity_who_categorized_article_id():
    """
    Returns the ID of the EntityWhoCategorizedArticle entry corresponding to the given AI name.
    If no matching row is found, returns None.
    """
    # Load environment variables
    load_dotenv()
    DB_DIR = os.getenv("PATH_DATABASE")
    DB_NAME = os.getenv("NAME_DB")
    AI_NAME = os.getenv("NAME_AI_ENTITY")
    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        # Step 1: Get ArtificialIntelligence.id
        ai_id_row = conn.execute(
            text("SELECT id FROM ArtificialIntelligences WHERE name = :name"),
            {"name": AI_NAME}
        ).fetchone()

        if not ai_id_row:
            print(f"No ArtificialIntelligence found with name '{AI_NAME}'.")
            return None

        ai_id = ai_id_row[0]

        # Step 2: Get EntityWhoCategorizedArticle.id using artificialIntelligenceId
        entity_row = conn.execute(
            text("SELECT id FROM EntityWhoCategorizedArticles WHERE artificialIntelligenceId = :ai_id LIMIT 1"),
            {"ai_id": ai_id}
        ).fetchone()

        if not entity_row:
            print(f"No EntityWhoCategorizedArticle found for artificialIntelligenceId '{ai_id}'.")
            return None

        return entity_row[0]


if __name__ == "__main__":
    main()