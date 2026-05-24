# banking-fraud-knowledge-graph
A Data Semantics project using OWL, RDF, GraphDB, and SPARQL to expose fraud-linked transaction patterns in banking data.
# Connecting the Dots: A Knowledge Graph for Exposing Fraud-Linked Transaction Patterns in Banking Data

Due to the size of the original IBM AML dataset (~5 million transactions), the full dataset is not included in this repository. The project uses a stratified sample containing all labelled laundering transactions and a subset of normal transactions for scalable RDF transformation and semantic querying.

**Original dataset source:
https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml**

## Overview

This project explores how semantic knowledge graphs can reduce fragmentation in anti-money laundering (AML) transaction data and improve the interpretability of suspicious financial behaviour.

Traditional relational datasets store financial transactions as isolated rows, making complex laundering structures difficult to detect without repeated joins and manual investigation. This project demonstrates how RDF knowledge graphs and semantic querying can expose hidden transaction relationships more transparently.

The project was developed for the **DS2526 Data Semantics** course at the **University of Milano-Bicocca (UNIMIB)**.

---

## Research Goal

The objective of this project is not to build a predictive fraud detection system, but to investigate how semantic modelling and graph traversal can support explainable exploration of suspicious financial transaction patterns.

The project focuses on three laundering structures:

* **FanOut** — one sender dispersing funds to multiple receivers
* **Cycle** — money circulating through accounts and returning to origin
* **GatherScatter** — funds collected into an intermediary account and redistributed outward

---

## Dataset

The project uses the **IBM Anti-Money Laundering Dataset** available on Kaggle.

### Dataset Characteristics

* ~5 million transactions
* 5,177 labelled laundering transactions
* Multiple payment formats
* Synthetic but structurally realistic AML behaviour

### Sampling Strategy

Due to the size of the full dataset, a stratified sample was used:

* All 5,177 labelled laundering transactions retained
* 5,000 randomly sampled non-laundering transactions included for behavioural contrast

Total transactions loaded into the graph:

* **10,177**

---

## Technologies Used

| Technology | Purpose                           |
| ---------- | --------------------------------- |
| Protégé    | Ontology modelling                |
| OWL        | Semantic ontology representation  |
| RDF        | Graph data representation         |
| GraphDB    | RDF triplestore                   |
| SPARQL     | Semantic querying                 |
| Python     | CSV → RDF transformation          |
| HermiT     | Ontology reasoning and validation |

---

## Ontology Design

The ontology models key banking and fraud-related entities including:

* Bank
* Account
* Transaction
* Currency
* PaymentFormat
* LaunderingPattern
* FraudIndicator

Key semantic modelling decisions:

* Domain and range restrictions
* Disjoint class axioms
* OWL reasoning validation using HermiT
* FIBO used as semantic reference vocabulary

---

## Project Pipeline

```text
Raw CSV Transaction Data
        ↓
Python RDF Conversion
        ↓
OWL Ontology in Protégé
        ↓
GraphDB Triplestore
        ↓
SPARQL Queries
        ↓
Fraud Pattern Analysis
```

---

## SPARQL Analysis

The project includes SPARQL queries for:

* Full transaction network exploration
* FanOut detection
* Cycle detection
* GatherScatter identification
* Fraud leaderboard ranking
* Pattern-level financial summaries

The semantic graph allows suspicious structures to be explored through linked relationships rather than isolated records.

---

## Repository Structure

```text
data/              → sampled datasets
ontology/          → OWL ontology files
documentation/     → SPARQL queries and project notes
presentation/      → presentation slides and report
python/            → RDF conversion scripts
```

---

## Current Status

Completed:

* Ontology modelling in Protégé
* RDF graph creation
* GraphDB integration
* SPARQL querying
* Manual fraud-pattern prototype
* Reasoner validation
* Project presentation

In progress:

* Python automation for scalable RDF generation
* Additional graph analytics queries

---

## Limitations

This project is a semantic systems prototype and has several limitations:

* Synthetic dataset
* No temporal reasoning engine
* Prototype-scale ontology
* Stratified sampling instead of full dataset loading
* No integration with real banking compliance systems

---

## Author

Victoria Bassey
MSc Data Science
University of Milano-Bicocca

Course:
DS2526 — Data Semantics
