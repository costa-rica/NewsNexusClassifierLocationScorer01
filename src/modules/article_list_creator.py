from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from transformers import pipeline
from tqdm import tqdm
import pandas as pd

def create_article_list(limit=None):
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

    # Load zero-shot classification model
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # Query articles with optional limit
    query = "SELECT id, description FROM Articles"
    if limit:
        query += f" LIMIT {limit}"

    with engine.connect() as conn:
        articles_list = conn.execute(text(query)).fetchall()

        # Initialize results_list, loading existing CSV if available
        existing_results_list = []
        processed_ids = set()
        if os.path.exists(CSV_PATH):
            try:
                existing_df = pd.read_csv(CSV_PATH)
                # results_list = existing_df.to_dict(orient="records")
                existing_results_list = existing_df.to_dict(orient="records")
                processed_ids = set(existing_df["article_id"].tolist())
                print(f"Loaded {len(existing_results_list)} existing records from {CSV_PATH}")
            except Exception as e:
                print(f"Could not load existing CSV: {e}")
        


    return articles_list, processed_ids, existing_results_list
    