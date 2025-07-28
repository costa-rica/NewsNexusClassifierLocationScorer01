from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from transformers import pipeline
from tqdm import tqdm
import pandas as pd

def create_article_list(entity_who_categorized_article_id, limit=None):
    # Load environment variables
    load_dotenv()

    # Paths from .env
    DB_DIR = os.getenv("PATH_DATABASE")
    DB_NAME = os.getenv("NAME_DB")
    CSV_DIR = os.getenv("PATH_OUTPUT_CLASSIFIER_LOCATION_SCORER")
    CSV_NAME = os.getenv("NAME_OUTPUT_CLASSIFIER_LOCATION_SCORER_FILE")

    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    CSV_PATH = os.path.join(CSV_DIR, CSV_NAME)

    # Connect to SQLite database
    engine = create_engine(f"sqlite:///{DB_PATH}")

    with engine.connect() as conn:
        # Get articleIds already analyzed by this entity
        excluded_ids = conn.execute(
            text("SELECT articleId FROM ArticleEntityWhoCategorizedArticleContracts WHERE entityWhoCategorizesId = :entity_id"),
            {"entity_id": entity_who_categorized_article_id}
        ).fetchall()

        excluded_ids = [row[0] for row in excluded_ids]

        # Query only articles not already analyzed
        query = "SELECT id, description, title FROM Articles"
        if excluded_ids:
            placeholders = ",".join(str(i) for i in excluded_ids)
            query += f" WHERE id NOT IN ({placeholders})"
        if limit:
            query += f" LIMIT {limit}"

        articles_list = conn.execute(text(query)).fetchall()

        # Initialize results_list, loading existing CSV if available
        existing_results_list = []
        processed_ids = set()
        if os.path.exists(CSV_PATH):
            try:
                existing_df = pd.read_csv(CSV_PATH)
                existing_results_list = existing_df.to_dict(orient="records")
                processed_ids = set(existing_df["article_id"].tolist())
                print(f"Loaded {len(existing_results_list)} existing records from {CSV_PATH}")
            except Exception as e:
                print(f"Could not load existing CSV: {e}")
        

    return articles_list, processed_ids, existing_results_list