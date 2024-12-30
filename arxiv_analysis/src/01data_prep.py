import os
import spacy
import pandas as pd

# Set display options to show full content except abstracts
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)  # Truncate long text to 50 characters

# Set up data access
current_dir = os.path.dirname(__file__)

DATA_DIR = os.path.join(current_dir, "..", "data")

ABSTRACT_FILE = os.path.join(DATA_DIR, "stat-abstracts.tsv")


# read the data

df = pd.read_csv(ABSTRACT_FILE, sep="\t", header=None)
df.columns = ["doc_id","title","category","abstract"]

print(df.head())
