# ============================================================
# Banking Fraud Knowledge Graph — Full RDF Conversion Script
# DS2526 Data Semantics Course Project
# ============================================================

import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, XSD

# ============================================================
# STEP 1: LOAD THE DATA
# ============================================================

print("Loading transaction data...")
trans_df = pd.read_csv("HI-Small_Trans.csv")
print(f"Total transactions loaded: {len(trans_df)}")

# ============================================================
# STEP 2: DATA QUALITY CHECK
# ============================================================

print("\n--- Missing Values ---")
print(trans_df.isnull().sum())

print("\n--- Data Types ---")
print(trans_df.dtypes)

print("\n--- Amount Paid (min, max) ---")
print("Min:", trans_df["Amount Paid"].min())
print("Max:", trans_df["Amount Paid"].max())
print("Negative amounts:", (trans_df["Amount Paid"] < 0).sum())

print("\n--- Amount Received (min, max) ---")
print("Min:", trans_df["Amount Received"].min())
print("Max:", trans_df["Amount Received"].max())
print("Negative amounts:", (trans_df["Amount Received"] < 0).sum())

print("\n--- Laundering breakdown ---")
print(trans_df["Is Laundering"].value_counts())

print("\n--- Payment formats ---")
print(trans_df["Payment Format"].value_counts())

print("\n--- Duplicate transactions ---")
print("Duplicates:", trans_df.duplicated().sum())

# ============================================================
# STEP 3: CLEAN THE DATA
# ============================================================

print("\nCleaning data...")

# Remove rows with missing values in key columns
before = len(trans_df)
trans_df = trans_df.dropna(subset=[
    "Timestamp", "From Bank", "Account",
    "To Bank", "Account.1", "Amount Paid",
    "Amount Received", "Payment Currency",
    "Receiving Currency", "Payment Format",
    "Is Laundering"
])
after = len(trans_df)
print(f"Rows removed due to missing values: {before - after}")

# Remove negative amounts
trans_df = trans_df[trans_df["Amount Paid"] >= 0]
trans_df = trans_df[trans_df["Amount Received"] >= 0]
print(f"Rows after removing negative amounts: {len(trans_df)}")

# Remove duplicate rows
trans_df = trans_df.drop_duplicates()
print(f"Rows after removing duplicates: {len(trans_df)}")

# Strip whitespace from text columns
trans_df["Payment Format"] = trans_df["Payment Format"].str.strip()
trans_df["Payment Currency"] = trans_df["Payment Currency"].str.strip()
trans_df["Receiving Currency"] = trans_df["Receiving Currency"].str.strip()
trans_df["Timestamp"] = trans_df["Timestamp"].str.strip()

print("Data cleaning complete.")

# ============================================================
# STEP 4: STRATIFIED SAMPLE
# ============================================================

print("\nTaking stratified sample...")

# Keep ALL laundering transactions
laundering = trans_df[trans_df["Is Laundering"] == 1]

# Take 5000 random normal transactions
normal = trans_df[trans_df["Is Laundering"] == 0].sample(
    n=5000, random_state=42
)

# Combine into one dataset
sampled = pd.concat([laundering, normal]).reset_index(drop=True)

print(f"Laundering transactions: {len(laundering)}")
print(f"Normal transactions:     {len(normal)}")
print(f"Total in sample:         {len(sampled)}")

# ============================================================
# STEP 5: SET UP RDF GRAPH AND ONTOLOGY NAMESPACE
# ============================================================

print("\nSetting up RDF graph...")

# This must match your Protege ontology IRI exactly
BFKG = Namespace("http://www.semanticweb.org/banking-fraud-kg#")

# Create empty graph and bind namespace
g = Graph()
g.bind("bfkg", BFKG)

# Sets to track already-created individuals (avoid duplicates)
created_banks = set()
created_accounts = set()
created_formats = set()
created_currencies = set()

# =====================