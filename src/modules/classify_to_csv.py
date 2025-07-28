from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from transformers import pipeline
from tqdm import tqdm
import pandas as pd

def classify_location_to_csv(articles_list, processed_ids, existing_results_list):
    # Load environment variables
    load_dotenv()

    # Paths from .env
    CSV_DIR = os.getenv("PATH_OUTPUT_CLASSIFIER_LOCATION_SCORER")
    CSV_NAME = os.getenv("NAME_OUTPUT_CLASSIFIER_LOCATION_SCORER_FILE")

    CSV_PATH = os.path.join(CSV_DIR, CSV_NAME)

    # Load zero-shot classification model
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


    total_articles = len(articles_list)
    progress_bar = tqdm(total=total_articles, desc="Classifying articles", unit="article")

    results_list = existing_results_list

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