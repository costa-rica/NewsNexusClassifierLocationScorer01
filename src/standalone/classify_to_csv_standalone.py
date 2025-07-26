from dotenv import load_dotenv
import os
import argparse
from sqlalchemy import create_engine, text
from transformers import pipeline
from tqdm import tqdm

# Load environment variables
load_dotenv()

parser = argparse.ArgumentParser(description="Run zero-shot classification with an optional limit.")
parser.add_argument("--limit", type=int, default=5, help="Number of articles to classify.")
args = parser.parse_args()
limit_count = args.limit

# Get paths from environment
db_dir = os.getenv("PATH_DATABASE")
db_name = os.getenv("NAME_DB")
db_path = os.path.join(db_dir, db_name)


# Get paths from environment
output_dir = os.getenv("PATH_OUTPUT_CLASSIFIER_LOCATION_SCORER")
output_name = os.getenv("NAME_OUTPUT_CLASSIFIER_LOCATION_SCORER_FILE")
csv_path = os.path.join(output_dir, output_name)


# Connect
engine = create_engine(f"sqlite:///{db_path}")

# Initialize zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Prepare result list
results_list = []

# Query all articles
with engine.connect() as conn:
    articles_list = conn.execute(
        text(f"SELECT id, description FROM Articles LIMIT {limit_count}")
    ).fetchall()

    # Use tqdm for progress bar
    for article in tqdm(articles_list, desc="Classifying articles", unit="article"):
        article_id = article.id
        description = article.description or ""

        # Classify description
        labels = ["Occurred in the United States", "Occurred outside the United States"]
        classification = classifier(description, candidate_labels=labels)

        # Get score for "Occurred in the United States"
        us_score = None
        for label, score in zip(classification["labels"], classification["scores"]):
            if label == "Occurred in the United States":
                us_score = score
                break

        # Append to results list
        results_list.append({
            "article_id": article_id,
            "score": us_score,
            "rating_for": "Occurred in the United States"
        })

# Save results to csv file
import pandas as pd
df = pd.DataFrame(results_list)
# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Save results to CSV file
df.to_csv(csv_path, index=False)
print(f"Results saved to {csv_path}")