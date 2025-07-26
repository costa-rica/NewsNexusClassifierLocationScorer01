# NewsNexusClassifierLocationScorer01

This is a Python application that uses the Huggingface zero-shot-classification pipeline to classify articles based on their location.

- Outside or inside the United States
- running the main.py file will classify all articles and write the results to the database
- model used: facebook/bart-large-mnli

## Make sure to run update_ai_entities.py first

This script will create the AI entity and the EntityWhoCategorizedArticles record in the database.

- This is a one-time operation
- `python src/standalone/update_ai_entities.py`

## Run the main app (main.py)

1. Set the environment variables in the .env file
2. Run the script

```bash
python src/main.py
```

- if you want to include a limit, you can do so by adding the --limit flag

```bash
python src/main.py --limit 10
```

## classify_to_csv_standalone.py

- for testing purpose -- no impact to database

### How to use classify_to_csv_standalone.py

1. Set the environment variables in the .env file
2. Run the script

```bash
python src/standalone/classify_to_csv_standalone.py
```

- By default, the script will classify the first 5 articles.

You can also specify the limit of articles to classify

```bash
python src/standalone/classify_to_csv_standalone.py --limit 10
```

## db_writer.py

This file contains the function write_scores_to_db_from_csv() that writes the scores to the database. It writes the scores to the ArticleEntityWhoCategorizedArticleContracts table from the output of the classify_to_csv.py script.

### How to use db_writer.py

1. Set the environment variables in the .env file
2. Run the script

```bash
python src/modules/db_writer.py
```

## .env file

```bash
NAME_DB=newsnexus07.db
PATH_DATABASE=/Users/nickrodriguez/Documents/_databases/NewsNexus07/
PATH_OUTPUT_CLASSIFIER_LOCATION_SCORER=/Users/nickrodriguez/Documents/_project_resources/NewsNexus07/utilities/classifier_location_scorer/
NAME_OUTPUT_CLASSIFIER_LOCATION_SCORER_FILE=location_classifier_output.csv
NAME_AI_ENTITY=NewsNexusClassifierLocationScorer01
```

## Folder Structure

```bash
NewsNexusClassifierLocationScorer01/
├── src/
│   ├── standalone/
│   │    ├── classify_to_csv_standalone.py   # optional legacy script
│   │    └── update_ai_entities.py
│   ├── modules/
│   │    ├── __init__.py
│   │    ├── classify_to_csv.py
│   │    └── db_writer.py
│   └── main.py
├── requirements.txt
└── README.md
```
