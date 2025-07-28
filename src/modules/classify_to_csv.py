from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from transformers import pipeline
from tqdm import tqdm
import pandas as pd

def classify_location_to_csv(limit=None):
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
        results_list = []
        processed_ids = set()
        if os.path.exists(CSV_PATH):
            try:
                existing_df = pd.read_csv(CSV_PATH)
                results_list = existing_df.to_dict(orient="records")
                processed_ids = set(existing_df["article_id"].tolist())
                print(f"Loaded {len(results_list)} existing records from {CSV_PATH}")
            except Exception as e:
                print(f"Could not load existing CSV: {e}")

        total_articles = len(articles_list)
        progress_bar = tqdm(total=total_articles, desc="Classifying articles", unit="article")

        for article in articles_list:
            # Skip if already processed
            if article.id in processed_ids:
                progress_bar.update(1)
                continue

            article_id = article.id
            description = article.description or ""

            # Skip if description is empty
            if not description.strip():
                progress_bar.update(1)
                continue

            # Define candidate labels
            labels = ["Occurred in the United States", "Occurred outside the United States"]

            # Perform classification
            classification = classifier(description, candidate_labels=labels)

            # Extract score for "Occurred in the United States"
            us_score = None
            for label, score in zip(classification["labels"], classification["scores"]):
                if label == "Occurred in the United States":
                    us_score = score
                    break

            # Append result
            results_list.append({
                "article_id": article_id,
                "score": us_score,
                "rating_for": "Occurred in the United States"
            })

            # Save progress every 10 articles
            if len(results_list) % 10 == 0:
                df_progress = pd.DataFrame(results_list)
                df_progress.to_csv(CSV_PATH, index=False)
                # print(f"Progress saved: {len(results_list)} records written to {CSV_PATH}")

            progress_bar.update(1)

        progress_bar.close()

    # Ensure output directory exists
    os.makedirs(CSV_DIR, exist_ok=True)

    # Save results to CSV
    df = pd.DataFrame(results_list)
    df.to_csv(CSV_PATH, index=False)

    print(f"Results saved to {CSV_PATH}")

if __name__ == "__main__":
    classify_location_to_csv()