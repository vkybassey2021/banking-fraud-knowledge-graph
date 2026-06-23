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

# Keep ALL laundering transactions (Minority class over-sampling)
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

# Pre-instantiate the patterns to anchor structural relationships
g.add((BFKG.Pattern_Laundering, RDF.type, BFKG.LaunderingPattern))
g.add((BFKG.Pattern_Normal, RDF.type, BFKG.LaunderingPattern))

# ============================================================
# STEP 6: ITERATE AND GENERATE TRIPLES (FIXED TEMPORAL LAYER)
# ============================================================

print("\nGenerating semantic triples...")

for idx, row in sampled.iterrows():
    # 1. Instantiate unique Transaction individual
    txn_uri = BFKG[f"Transaction_{idx:06d}"]
    g.add((txn_uri, RDF.type, BFKG.Transaction))
    
    # 2. Financial Metrics Data Properties
    g.add((txn_uri, BFKG.hasAmountPaid, Literal(row["Amount Paid"], datatype=XSD.decimal)))
    g.add((txn_uri, BFKG.hasAmountReceived, Literal(row["Amount Received"], datatype=XSD.decimal)))
    
    # 3. CRITICAL FIXED: ISO 8601 xsd:dateTime Transformation
    try:
        # Convert raw text string safely to datetime object
        dt_obj = pd.to_datetime(row["Timestamp"])
        # Format string to strict: YYYY-MM-DDThh:mm:ssZ
        iso_timestamp = dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        # Assert explicitly into the graph using XSD.dateTime
        g.add((txn_uri, BFKG.hasTimestamp, Literal(iso_timestamp, datatype=XSD.dateTime)))
    except Exception as e:
        print(f"Warning: Failed to parse timestamp for index {idx}, fallback to original string context.")
        g.add((txn_uri, BFKG.hasTimestamp, Literal(row["Timestamp"], datatype=XSD.string)))

    # 4. Currency Entities & Object Properties
    pay_curr_name = row["Payment Currency"].replace(" ", "_")
    rec_curr_name = row["Receiving Currency"].replace(" ", "_")
    pay_curr_uri = BFKG[pay_curr_name]
    rec_curr_uri = BFKG[rec_curr_name]
    
    if pay_curr_name not in created_currencies:
        g.add((pay_curr_uri, RDF.type, BFKG.Currency))
        created_currencies.add(pay_curr_name)
    if rec_curr_name not in created_currencies:
        g.add((rec_curr_uri, RDF.type, BFKG.Currency))
        created_currencies.add(rec_curr_name)
        
    g.add((txn_uri, BFKG.hasPaymentCurrency, pay_curr_uri))
    g.add((txn_uri, BFKG.hasReceivingCurrency, rec_curr_uri))

    # 5. Payment Format Entities & Object Properties
    fmt_name = row["Payment Format"].replace(" ", "_")
    fmt_uri = BFKG[fmt_name]
    if fmt_name not in created_formats:
        g.add((fmt_uri, RDF.type, BFKG.PaymentFormat))
        created_formats.add(fmt_name)
    g.add((txn_uri, BFKG.hasPaymentFormat, fmt_uri))

    # 6. Banking Institution Entities
    from_bank_id = f"Bank_{int(row['From Bank'])}"
    to_bank_id = f"Bank_{int(row['To Bank'])}"
    from_bank_uri = BFKG[from_bank_id]
    to_bank_uri = BFKG[to_bank_id]
    
    if from_bank_id not in created_banks:
        g.add((from_bank_uri, RDF.type, BFKG.Bank))
        created_banks.add(from_bank_id)
    if to_bank_id not in created_banks:
        g.add((to_bank_uri, RDF.type, BFKG.Bank))
        created_banks.add(to_bank_id)

    # 7. Account Entities & Institutional Bindings
    snd_acc_id = f"Account_{row['Account']}"
    rcv_acc_id = f"Account_{row['Account.1']}"
    snd_acc_uri = BFKG[snd_acc_id]
    rcv_acc_uri = BFKG[rcv_acc_id]
    
    if snd_acc_id not in created_accounts:
        g.add((snd_acc_uri, RDF.type, BFKG.Account))
        g.add((snd_acc_uri, BFKG.belongsToBank, from_bank_uri))
        created_accounts.add(snd_acc_id)
    if rcv_acc_id not in created_accounts:
        g.add((rcv_acc_uri, RDF.type, BFKG.Account))
        g.add((rcv_acc_uri, BFKG.belongsToBank, to_bank_uri))
        created_accounts.add(rcv_acc_id)
        
    g.add((txn_uri, BFKG.hasSenderAccount, snd_acc_uri))
    g.add((txn_uri, BFKG.hasReceiverAccount, rcv_acc_uri))

    # 8. Structural Relationship Mapping for TBox Inference Engine
    if row["Is Laundering"] == 1:
        # Link directly to the laundering pattern entity
        g.add((txn_uri, BFKG.belongsToPattern, BFKG.Pattern_Laundering))
        # Optional backward compatibility triple
        g.add((txn_uri, BFKG.isLaundering, Literal(True, datatype=XSD.boolean)))
    else:
        g.add((txn_uri, BFKG.belongsToPattern, BFKG.Pattern_Normal))
        g.add((txn_uri, BFKG.isLaundering, Literal(False, datatype=XSD.boolean)))

print("Triple generation complete.")

# ============================================================
# STEP 7: SERIALIZE AND SAVE KNOWLEDGE GRAPH
# ============================================================

output_filename = "banking_fraud_kg_full_fixed.ttl"
print(f"\nSerializing graph to {output_filename} (Turtle format)...")
g.serialize(destination=output_filename, format="turtle")
print("Serialization complete. Graph structure is now fully valid and optimized for temporal reasoning!")