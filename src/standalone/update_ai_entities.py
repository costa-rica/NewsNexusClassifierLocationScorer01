from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
# Current timestamp
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " +00:00"
# Get database path
DB_DIR = os.getenv("PATH_DATABASE")
DB_NAME = os.getenv("NAME_DB")
DB_PATH = os.path.join(DB_DIR, DB_NAME)
NAME_AI_ENTITY = os.getenv("NAME_AI_ENTITY")

# Connect to SQLite
engine = create_engine(f"sqlite:///{DB_PATH}")

# Values to insert
ai_name = NAME_AI_ENTITY
ai_description = (
    "zero shot classifier model with classifications for 1. Occurred in the United States "
    "and 2. Occurred outside the United States"
)
ai_model_name = "facebook/bart-large-mnli"
ai_model_type = "zero-shot-classification"

with engine.begin() as conn:
    # Check if AI entry already exists
    check_ai = text("SELECT id FROM ArtificialIntelligences WHERE name = :name")
    existing_ai = conn.execute(check_ai, {"name": ai_name}).fetchone()

    if existing_ai:
        print(f"ArtificialIntelligence with name '{ai_name}' already exists. Exiting script.")
        exit(0)

    # Insert into ArtificialIntelligences
    insert_ai = text("""
        INSERT INTO ArtificialIntelligences
        (name, description, huggingFaceModelName, huggingFaceModelType, createdAt, updatedAt)
        VALUES (:name, :description, :model_name, :model_type, :created_at, :updated_at)
    """)

    conn.execute(insert_ai, {
        "name": ai_name,
        "description": ai_description,
        "model_name": ai_model_name,
        "model_type": ai_model_type,
        "created_at": now,
        "updated_at": now
    })

    # Get last inserted ID
    ai_id_result = conn.execute(text("SELECT last_insert_rowid()"))
    ai_id = ai_id_result.scalar()

    # Insert into EntityWhoCategorizedArticles
    insert_entity = text("""
        INSERT INTO EntityWhoCategorizedArticles (artificialIntelligenceId, createdAt, updatedAt)
        VALUES (:ai_id, :created_at, :updated_at)
    """)
    conn.execute(insert_entity, {
        "ai_id": ai_id,
        "created_at": now,
        "updated_at": now
    })

print("Inserted new ArtificialIntelligence and EntityWhoCategorizedArticles rows.")