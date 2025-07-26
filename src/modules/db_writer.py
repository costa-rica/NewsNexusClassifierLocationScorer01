from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

def write_scores_to_db_from_csv():
    # Load environment variables
    load_dotenv()

    # Paths from .env
    DB_DIR = os.getenv("PATH_DATABASE")
    DB_NAME = os.getenv("NAME_DB")
    CSV_DIR = os.getenv("PATH_OUTPUT_CLASSIFIER_LOCATION_SCORER")
    CSV_NAME = os.getenv("NAME_OUTPUT_CLASSIFIER_LOCATION_SCORER_FILE")
    AI_NAME = os.getenv("NAME_AI_ENTITY")

    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    CSV_PATH = os.path.join(CSV_DIR, CSV_NAME)

    # Connect to SQLite
    engine = create_engine(f"sqlite:///{DB_PATH}")
    duplicate_count = 0
    df_len = 0
    with engine.begin() as conn:
        # Current timestamp
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " +00:00"
        # 1. Get AI row ID
        ai_query = text("SELECT id FROM ArtificialIntelligences WHERE name = :name")
        ai_row = conn.execute(ai_query, {"name": AI_NAME}).fetchone()

        if not ai_row:
            raise ValueError(f"No ArtificialIntelligence row found for name '{AI_NAME}'")

        ai_id = ai_row.id

        # 2. Get entityWhoCategorizedId
        entity_query = text("""
            SELECT id FROM EntityWhoCategorizedArticles
            WHERE artificialIntelligenceId = :ai_id
        """)
        entity_row = conn.execute(entity_query, {"ai_id": ai_id}).fetchone()

        if not entity_row:
            raise ValueError(f"No EntityWhoCategorizedArticles row found for AI id '{ai_id}'")

        entity_id = entity_row.id

        # 3. Read CSV
        df = pd.read_csv(CSV_PATH)
        df_len = len(df)
        # 4. Insert rows into ArticleEntityWhoCategorizedArticleContract
        for _, row in df.iterrows():
            try:
                insert_stmt = text("""
                    INSERT INTO ArticleEntityWhoCategorizedArticleContracts
                    (articleId, entityWhoCategorizesId, keyword, keywordRating, createdAt, updatedAt)
                    VALUES (:article_id, :entity_id, :keyword, :rating, :created_at, :updated_at)
                """)
                conn.execute(insert_stmt, {
                    "article_id": int(row["article_id"]),
                    "entity_id": entity_id,
                    "keyword": row["rating_for"],
                    "rating": float(row["score"]),
                    "created_at": now,
                    "updated_at": now
                })
            except IntegrityError:
                # Skip duplicates and continue
                duplicate_count += 1
                continue

    
    if df_len == duplicate_count:
        print(f"All data was duplicates. No data was written to the database.")
    elif duplicate_count > 0:
        print(f"There existed {duplicate_count} duplicates. These were skipped.")
    else:
        print(f"{df_len} rows were written to the database.")

    print("Completed write_scores_to_db_from_csv function.")

if __name__ == "__main__":
    write_scores_to_db_from_csv()
