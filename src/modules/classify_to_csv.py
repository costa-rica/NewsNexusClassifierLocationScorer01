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

        results_list = []

        # Use tqdm for progress bar
        for article in tqdm(articles_list, desc="Classifying articles", unit="article"):
            article_id = article.id
            description = article.description or ""

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

    # Ensure output directory exists
    os.makedirs(CSV_DIR, exist_ok=True)

    # Save results to CSV
    df = pd.DataFrame(results_list)
    df.to_csv(CSV_PATH, index=False)

    print(f"Results saved to {CSV_PATH}")

if __name__ == "__main__":
    classify_location_to_csv()