# FinGuard — AWS Data Engineering Pipeline

FinGuard is an end-to-end **AWS Data Engineering portfolio project** that builds a cloud-based data lake and processing pipeline using a financial transactions and fraud dataset.

The project demonstrates how external datasets can be ingested into **Amazon S3**, profiled and validated, and transformed using **AWS Glue and Apache Spark** into **Apache Iceberg tables** following a Medallion-style architecture.

The current implementation supports:

* Kaggle dataset ingestion
* Amazon S3 Landing layer
* Date-partitioned raw data storage
* Automated Landing-layer data profiling
* AWS Glue / PySpark transformations
* Explicit Spark schemas
* Apache Iceberg Bronze tables
* AWS Glue Data Catalog integration
* Bronze ingestion metadata

The project will progressively introduce Silver and Gold transformations, data quality controls, orchestration, analytics, monitoring, and CI/CD.

---

# 1. Architecture

The current implemented pipeline is:

```text
                    Kaggle
                      │
                      │ Python / KaggleHub
                      ▼
             ┌──────────────────┐
             │   Python          │
             │   Ingestion       │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │    Amazon S3     │
             │  Landing Layer   │
             │                  │
             │   CSV / JSON     │
             └────────┬─────────┘
                      │
                Data Profiling
                      │
                      ▼
             ┌──────────────────┐
             │    AWS Glue      │
             │     PySpark      │
             │                  │
             │ Explicit Schemas │
             │ Metadata Columns │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │      Bronze      │
             │                  │
             │ Apache Iceberg   │
             │    Parquet       │
             │ Iceberg Format 2 │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ AWS Glue Data    │
             │     Catalog      │
             │                  │
             │ finguard_bronze  │
             └────────┬─────────┘
                      │
                      ▼
              Silver — Planned
                      │
                      ▼
               Gold — Planned
                      │
                      ▼
             Athena / Analytics
```

---

# 2. Project Objectives

The objective of FinGuard is to build a realistic cloud Data Engineering pipeline demonstrating modern AWS data engineering practices.

The project is designed to demonstrate:

* Python-based data ingestion
* Kaggle dataset integration
* AWS S3 data lake design
* Configuration-driven ingestion
* Date-partitioned Landing data
* Reusable Python components
* Pandas-based data profiling
* AWS Glue ETL
* Apache Spark / PySpark
* Explicit schema definition
* Apache Iceberg
* Parquet storage
* AWS Glue Data Catalog
* Medallion architecture
* Data quality validation
* Pipeline observability
* Cloud-native Data Engineering practices

The ingestion layer is intentionally designed so that it can support multiple datasets rather than being tightly coupled to a single source file.

---

# 3. Dataset

The project currently uses the Kaggle:

**Transactions Fraud Dataset**

```text
computingvictor/transactions-fraud-datasets
```

The dataset contains financial transaction, customer, card, merchant-category and fraud-related data.

The ingestion process currently handles the following source files:

```text
cards_data.csv
mcc_codes.json
train_fraud_labels.json
transactions_data.csv
users_data.csv
```

These are mapped to corresponding S3 Landing locations:

```python
File_Mappings = {
    "cards_data.csv":
        "landing/cards_data",

    "mcc_codes.json":
        "landing/mcc_codes",

    "train_fraud_labels.json":
        "landing/train_fraud_labels",

    "transactions_data.csv":
        "landing/transactions_data",

    "users_data.csv":
        "landing/users_data"
}
```

The mapping represents:

```text
Source filename
        │
        ▼
S3 Landing prefix
```

This keeps dataset-specific configuration separate from the reusable ingestion implementation.

---

# 4. Medallion Data Architecture

FinGuard uses a Medallion-style data architecture.

```text
Landing
   │
   ▼
Bronze
   │
   ▼
Silver
   │
   ▼
Gold
```

The layers have different responsibilities.

---

## 4.1 Landing Layer

The Landing layer contains the source data in its original format.

The project currently supports:

```text
CSV
JSON
```

Example structure:

```text
s3://finguard-data/

landing/
│
├── cards_data/
│   └── ingestion_date=YYYY-MM-DD/
│       └── cards_data.csv
│
├── transactions_data/
│   └── ingestion_date=YYYY-MM-DD/
│       └── transactions_data.csv
│
├── users_data/
│   └── ingestion_date=YYYY-MM-DD/
│       └── users_data.csv
│
├── mcc_codes/
│   └── ingestion_date=YYYY-MM-DD/
│       └── mcc_codes.json
│
└── train_fraud_labels/
    └── ingestion_date=YYYY-MM-DD/
        └── train_fraud_labels.json
```

Source data is preserved before downstream transformations.

This provides:

* Source traceability
* Historical auditing
* Pipeline replay
* Recovery from downstream failures
* Easier debugging
* Separation between ingestion and transformation

Each ingestion run uses:

```text
ingestion_date=YYYY-MM-DD
```

as part of the S3 object key.

---

# 5. Kaggle → S3 Ingestion

The ingestion pipeline is implemented in:

```text
src/fin_guard/scripts/ingest.py
```

The ingestion process performs:

```text
Kaggle
   │
   ▼
Download Dataset
   │
   ▼
Discover Configured Files
   │
   ▼
Build S3 Object Keys
   │
   ▼
Upload Files
   │
   ▼
S3 Landing Layer
```

---

## Step 1 — Download the Dataset

The dataset is downloaded programmatically:

```python
dataset_path = download_dataset(DATASET_HANDLE)
```

Current dataset:

```python
DATASET_HANDLE = "computingvictor/transactions-fraud-datasets"
```

---

## Step 2 — Discover Files

The downloaded directory is inspected for configured source files.

```python
dataset_files = discover_files(
    dataset_path,
    File_Mappings
)
```

Each discovered file is represented using structured file metadata.

This separates file discovery from the upload implementation.

---

## Step 3 — Build the S3 Object Key

The S3 uploader generates date-partitioned keys.

For example:

```text
landing/cards_data/
    ingestion_date=2026-09-18/
        cards_data.csv
```

Resulting in:

```text
s3://finguard-data/landing/cards_data/ingestion_date=2026-09-18/cards_data.csv
```

---

## Step 4 — Upload to S3

Files are uploaded using `boto3`.

```python
upload_file(
    dataset_file=dataset_file,
    bucket_name=BUCKET_NAME
)
```

AWS authentication is handled through the standard AWS SDK credential provider chain.

AWS credentials are **not stored in the project source code**.

---

# 6. Landing Data Profiling

Before processing data into Bronze, the project provides a Landing-layer profiling utility:

```text
src/fin_guard/scripts/profile_dataset.py
```

The profiler scans supported files under:

```text
s3://finguard-data/landing/
```

and performs basic dataset-level inspection.

For each dataset it reports:

```text
Sample records
Column names
Data types
Null counts
Duplicate counts
```

Example:

```text
================================================================================
FILE: landing/cards_data/ingestion_date=2026-09-18/cards_data.csv
================================================================================

--- SAMPLE RECORDS ---

...

--- COLUMN NAMES ---

...

--- Data Types ---

...

--- Null Checks ---

...

--- Duplicate checks ---

number of duplicates: ...
```

The profiler supports both:

```text
CSV
JSON
```

including JSON structures such as MCC code mappings and nested fraud-label mappings.

This provides an initial understanding of source-data structure and quality before transformation.

---

# 7. Landing → Bronze Processing

The Landing-to-Bronze transformation is implemented using:

```text
AWS Glue
Apache Spark / PySpark
Apache Iceberg
AWS Glue Data Catalog
Amazon S3
```

Current Glue jobs:

```text
src/glue/
│
├── landing_to_bronze_cards.py
│
└── landing_to_bronze_transactions.py
```

These jobs currently process:

```text
cards_data.csv
transactions_data.csv
```

---

# 8. AWS Glue Processing

Each AWS Glue job performs the following workflow:

```text
Today's Landing Partition
          │
          ▼
     Read CSV
          │
          ▼
Apply Explicit Spark Schema
          │
          ▼
Add Bronze Metadata
          │
          ▼
Create Iceberg Table
          │
          ▼
Write Parquet Data to S3
          │
          ▼
Register Table in
AWS Glue Data Catalog
```

The jobs determine the current ingestion date:

```python
ingestion_date = date.today().isoformat()
```

and read the corresponding Landing partition.

For example:

```text
s3://finguard-data/landing/cards_data/
    ingestion_date=YYYY-MM-DD/
```

and:

```text
s3://finguard-data/landing/transactions_data/
    ingestion_date=YYYY-MM-DD/
```

---

# 9. Explicit Spark Schemas

The Glue jobs use explicit Spark schemas rather than relying on automatic schema inference.

For example, the transaction schema defines fields including:

```text
id
date
client_id
card_id
amount
use_chip
merchant_id
merchant_city
merchant_state
zip
mcc
errors
```

using Spark data types such as:

```text
LongType
IntegerType
DoubleType
StringType
TimestampType
```

Similarly, the card dataset defines fields including:

```text
id
client_id
card_brand
card_type
card_number
expires
cvv
has_chip
num_cards_issued
credit_limit
acct_open_date
year_pin_last_changed
card_on_dark_web
```

Using explicit schemas provides:

* Predictable data types
* Schema control
* Better failure detection
* Reduced schema inference overhead
* More deterministic downstream processing

---

# 10. Bronze Metadata

The Glue jobs enrich source records with ingestion metadata.

The following columns are currently added:

```text
ingestion_date
bronze_ingestion_timestamp
source_file
```

### `ingestion_date`

Identifies the source ingestion date.

```python
.withColumn(
    "ingestion_date",
    to_date(lit(ingestion_date))
)
```

### `bronze_ingestion_timestamp`

Records when the row was processed into Bronze.

```python
.withColumn(
    "bronze_ingestion_timestamp",
    current_timestamp()
)
```

### `source_file`

Captures the original S3 source file.

```python
.withColumn(
    "source_file",
    input_file_name()
)
```

These fields provide lineage and auditability between Landing and Bronze.

---

# 11. Apache Iceberg Bronze Layer

The Bronze layer uses **Apache Iceberg rather than standalone Parquet files**.

Iceberg manages the table while Parquet is used as the underlying data-file format.

Conceptually:

```text
                 Apache Iceberg Table
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    Iceberg Metadata              Parquet Files
           │                           │
           └─────────────┬─────────────┘
                         ▼
                      Amazon S3
```

Current Bronze storage locations include:

```text
s3://finguard-data/bronze/cards_data/
```

and:

```text
s3://finguard-data/bronze/transactions_data/
```

---

# 12. Iceberg Table Configuration

The current implementation uses:

```text
Apache Iceberg format-version = 2
```

For example:

```python
.tableProperty(
    "format-version",
    "2"
)
```

The tables are partitioned by:

```text
ingestion_date
```

using:

```python
.partitionedBy(
    col("ingestion_date")
)
```

Iceberg provides table-management capabilities beyond simply storing Parquet files, including:

* ACID transactions
* Schema evolution
* Partition evolution
* Snapshot management
* Time travel
* Reliable metadata management
* Atomic table operations

---

# 13. AWS Glue Data Catalog

Bronze Iceberg tables are registered with the AWS Glue Data Catalog.

The catalog database is:

```text
finguard_bronze
```

Current tables are:

```text
finguard_bronze.cards_data
finguard_bronze.transactions
```

The Spark identifiers used by the Glue jobs are:

```text
glue_catalog.finguard_bronze.cards_data
```

and:

```text
glue_catalog.finguard_bronze.transactions
```

This provides a centralized metadata catalog that can later be queried by engines such as Amazon Athena.

---

# 14. Current Bronze Tables

## Cards

Source:

```text
landing/cards_data/
```

Glue job:

```text
landing_to_bronze_cards.py
```

Iceberg table:

```text
finguard_bronze.cards_data
```

Storage:

```text
s3://finguard-data/bronze/cards_data/
```

---

## Transactions

Source:

```text
landing/transactions_data/
```

Glue job:

```text
landing_to_bronze_transactions.py
```

Iceberg table:

```text
finguard_bronze.transactions
```

Storage:

```text
s3://finguard-data/bronze/transactions_data/
```

---

# 15. Current Project Structure

The repository currently contains:

```text
FinGuard_AWS_Project/
│
├── .gitignore
├── Readme.MD
├── pyproject.toml
├── uv.lock
│
└── src/
    │
    ├── fin_guard/
    │   │
    │   ├── __init__.py
    │   │
    │   ├── ingestion/
    │   │   │
    │   │   ├── __init__.py
    │   │   ├── file_discovery.py
    │   │   ├── kaggle_client.py
    │   │   └── s3_uploader.py
    │   │
    │   └── scripts/
    │       │
    │       ├── ingest.py
    │       └── profile_dataset.py
    │
    └── glue/
        │
        ├── landing_to_bronze_cards.py
        └── landing_to_bronze_transactions.py
```

---

# 16. Technology Stack

| Technology             | Purpose                                  |
| ---------------------- | ---------------------------------------- |
| Python                 | Ingestion and data utilities             |
| uv                     | Python dependency/environment management |
| Kaggle / KaggleHub     | External dataset source                  |
| Pandas                 | Landing-layer profiling                  |
| boto3                  | AWS SDK / S3 interaction                 |
| Amazon S3              | Data lake storage                        |
| AWS Glue               | Managed ETL processing                   |
| Apache Spark / PySpark | Distributed data transformation          |
| Apache Parquet         | Physical columnar data storage           |
| Apache Iceberg         | Data lake table format                   |
| AWS Glue Data Catalog  | Iceberg table metadata/catalog           |
| Git / GitHub           | Source control                           |

Planned technologies include:

```text
Amazon Athena
Apache Airflow
AWS CloudWatch
GitHub Actions
Infrastructure as Code
```

---

# 17. Running the Local Ingestion Pipeline

## Prerequisites

The following are required:

```text
Python
uv
AWS account
AWS CLI
Kaggle access
```

Verify the AWS identity:

```bash
aws sts get-caller-identity
```

Verify the configured AWS region:

```bash
aws configure get region
```

---

## Install Dependencies

Using `uv`:

```bash
uv sync
```

Dependencies are managed through:

```text
pyproject.toml
uv.lock
```

---

## Run the Ingestion Pipeline

From the project root:

```bash
uv run python src/fin_guard/scripts/ingest.py
```

The pipeline performs:

```text
1. Download Kaggle dataset
2. Discover configured files
3. Build S3 object keys
4. Upload source files to Landing
5. List uploaded S3 objects
```

---

# 18. Run the Landing Data Profiler

The Landing profiler can be executed using:

```bash
uv run python src/fin_guard/scripts/profile_dataset.py
```

It scans:

```text
s3://finguard-data/landing/
```

and reports:

```text
Sample records
Columns
Data types
Null values
Duplicate records
```

for supported source files.

---

# 19. Running AWS Glue Jobs

## Deploying and Updating AWS Glue Jobs Using AWS CLI

AWS Glue PySpark scripts are developed locally in **VS Code** and deployed to Amazon S3 using the **AWS Command Line Interface (AWS CLI)**.

The deployment flow is:

```text
VS Code / Local Development
          │
          ▼
     src/glue/
          │
          │ AWS CLI
          ▼
  S3 glue-scripts/
          │
          ▼
      AWS Glue Job
          │
          ▼
Landing → Bronze Iceberg
```

### Upload Glue Scripts to S3

After developing or modifying a Glue script locally, the latest version is copied to the S3 Glue scripts location using the AWS CLI.

Transactions:

```bash
aws s3 cp \
  src/glue/landing_to_bronze_transactions.py \
  s3://finguard-data/glue-scripts/landing_to_bronze_transactions.py
```

Cards:

```bash
aws s3 cp \
  src/glue/landing_to_bronze_cards.py \
  s3://finguard-data/glue-scripts/landing_to_bronze_cards.py
```

The Glue scripts are stored in:

```text
s3://finguard-data/glue-scripts/
├── landing_to_bronze_cards.py
└── landing_to_bronze_transactions.py
```

### Updating AWS Glue Jobs

The AWS CLI is also used to update existing Glue jobs so that they reference the latest script stored in Amazon S3.

General command:

```bash
aws glue update-job \
  --job-name <glue-job-name> \
  --job-update '{
    "Command": {
      "Name": "glueetl",
      "ScriptLocation": "s3://finguard-data/glue-scripts/<script-name>.py",
      "PythonVersion": "3"
    }
  }'
```

This provides a repeatable command-line deployment workflow:

```text
Develop / update PySpark script in VS Code
                    │
                    ▼
Commit source code to Git
                    │
                    ▼
Upload script to S3 using AWS CLI
                    │
                    ▼
Update AWS Glue job using AWS CLI
                    │
                    ▼
Run Glue ETL job
                    │
                    ▼
Transform Landing data
                    │
                    ▼
Write Bronze Apache Iceberg table
```

This approach keeps the Glue ETL source code version-controlled in Git while using Amazon S3 as the deployment location for AWS Glue. It also provides a foundation for automating Glue deployments through CI/CD in future iterations of the project.

---

# 20. Current End-to-End Data Flow

The implemented pipeline can currently be summarized as:

```text
computingvictor/transactions-fraud-datasets
                    │
                    ▼
              KaggleHub
                    │
                    ▼
             Python Ingestion
                    │
                    ▼
              Amazon S3
             Landing Layer
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     cards_data          transactions_data
          │                   │
          ▼                   ▼
     AWS Glue             AWS Glue
       PySpark              PySpark
          │                   │
          ▼                   ▼
   Explicit Schema      Explicit Schema
          │                   │
          ▼                   ▼
    Bronze Metadata      Bronze Metadata
          │                   │
          ▼                   ▼
     Iceberg v2           Iceberg v2
          │                   │
          ▼                   ▼
   bronze/cards_data   bronze/transactions_data
          │                   │
          └─────────┬─────────┘
                    ▼
            AWS Glue Catalog
                    │
                    ▼
             finguard_bronze
```

---

# 21. Why Keep a Landing Layer?

The Landing layer preserves the original source data before transformations.

This enables:

* Pipeline replay
* Auditing
* Source traceability
* Debugging
* Recovery from downstream failures
* Reprocessing with updated business rules

The Landing layer therefore acts as the immutable entry point into the data lake.

---

# 22. Why Partition Landing Data by Ingestion Date?

The Landing S3 layout uses:

```text
ingestion_date=YYYY-MM-DD
```

This allows ingestion runs to be logically separated.

It supports:

* Historical investigation
* Incremental processing
* Pipeline replay
* Auditing
* Easier identification of ingestion batches

---

# 23. Why Apache Iceberg?

Parquet provides an efficient columnar file format, but Parquet alone does not provide table-level transaction management.

Apache Iceberg adds a table-management layer over the underlying Parquet files.

This provides capabilities such as:

```text
ACID transactions
Schema evolution
Partition evolution
Snapshots
Time travel
Atomic writes
Metadata management
```

This makes the Bronze layer behave more like a managed analytical table rather than simply a directory containing Parquet files.

---

# 24. Data Quality Strategy

The project currently includes basic Landing-layer profiling.

Current profiling includes:

```text
Schema inspection
Data type inspection
Null counts
Duplicate detection
Sample record inspection
```

Future data-quality rules will include:

```text
Required-field validation
Business-rule validation
Data type validation
Referential integrity
Invalid-record handling
Source-to-target reconciliation
Schema drift detection
```

Pydantic may be used for selected field-level validation, while Pandas and Spark can perform dataset-level validation.

Invalid records may eventually be written to a quarantine area:

```text
s3://finguard-data/quarantine/
```

rather than being silently discarded.

---

# 25. Silver Layer — Planned

The Silver layer will transform Bronze data into cleaned, validated and standardized datasets.

Potential transformations include:

```text
Bronze
   │
   ├── Clean monetary values
   ├── Normalize dates
   ├── Handle nulls
   ├── Remove duplicates
   ├── Validate card/customer relationships
   ├── Standardize merchant information
   ├── Join MCC descriptions
   ├── Apply fraud labels
   └── Apply data-quality rules
          │
          ▼
       Silver
```

Silver tables will also use Apache Iceberg.

---

# 26. Gold Layer — Planned

The Gold layer will contain business and analytics-oriented datasets derived from Silver.

Potential analytical models include:

```text
customer_transaction_summary
merchant_transaction_summary
fraud_transaction_summary
daily_transaction_summary
card_usage_summary
fraud_by_merchant_category
fraud_by_transaction_type
```

These datasets can then support:

```text
Amazon Athena
BI dashboards
Financial analytics
Fraud analytics
Machine learning
Reporting
```

---

# 27. Current Implementation Status

## Ingestion

* [x] Kaggle dataset download
* [x] Generic file discovery
* [x] Configuration-based file mappings
* [x] S3 Landing layer
* [x] Date-partitioned Landing ingestion
* [x] Multiple source file support
* [x] CSV ingestion
* [x] JSON ingestion

## Data Profiling

* [x] Landing S3 file discovery
* [x] CSV profiling
* [x] JSON profiling
* [x] Column inspection
* [x] Data type inspection
* [x] Null analysis
* [x] Duplicate detection

## Bronze

* [x] AWS Glue jobs
* [x] PySpark transformations
* [x] Explicit Spark schemas
* [x] Cards Landing → Bronze
* [x] Transactions Landing → Bronze
* [x] Bronze ingestion metadata
* [x] Apache Iceberg tables
* [x] Iceberg format version 2
* [x] Parquet-backed storage
* [x] `ingestion_date` partitioning
* [x] AWS Glue Data Catalog integration

## Planned

* [ ] Incremental Iceberg append/upsert strategy
* [ ] Users Landing → Bronze
* [ ] MCC codes Landing → Bronze
* [ ] Fraud labels Landing → Bronze
* [ ] Silver transformation layer
* [ ] Gold analytical models
* [ ] Amazon Athena querying
* [ ] Pydantic field validation
* [ ] Automated data quality framework
* [ ] Quarantine/error handling
* [ ] Apache Airflow orchestration
* [ ] Unit tests
* [ ] Integration tests
* [ ] CI/CD pipeline
* [ ] CloudWatch logging and monitoring
* [ ] Infrastructure as Code

---

# 28. Current Limitation — Iceberg Incremental Loads

The current Glue implementation creates the Bronze Iceberg tables using:

```python
.writeTo(table_name)
.using("iceberg")
...
.create()
```

This is suitable for the **initial creation of the Iceberg table**.

A production-style implementation must also handle subsequent ingestion runs.

Future versions will introduce an incremental loading strategy such as:

```text
First run
    │
    └── CREATE Iceberg table

Subsequent runs
    │
    ├── APPEND
    │
    └── or MERGE INTO
```

The appropriate strategy will depend on whether the source represents append-only data or requires updates/deduplication.

---

# 29. Engineering Principles

The project aims to demonstrate several production Data Engineering principles.

### Separation of Concerns

Dataset download, file discovery, S3 upload, profiling, schema definition and transformation are implemented as separate responsibilities.

### Configuration Over Hardcoding

Dataset-specific file mappings are separated from reusable ingestion logic.

### Raw Data Preservation

Original source data is retained in the Landing layer.

### Explicit Schemas

Bronze ingestion uses explicit Spark schemas rather than depending entirely on automatic schema inference.

### Data Lineage

Metadata fields such as:

```text
ingestion_date
source_file
bronze_ingestion_timestamp
```

allow Bronze records to be traced back to their source ingestion.

### Open Table Formats

Apache Iceberg provides a managed table abstraction over Parquet data stored in Amazon S3.

### Idempotency

Future pipeline versions will ensure that rerunning ingestion and transformation jobs does not unintentionally duplicate or corrupt data.

### Observability

Structured logging, metrics, Glue job monitoring and CloudWatch integration will be introduced as the pipeline evolves.

### Testability

Core ingestion and transformation components should be independently testable.

---

# 30. Target Architecture

The longer-term target architecture is:

```text
                           Kaggle
                              │
                              ▼
                       Python Ingestion
                              │
                              ▼
                   ┌─────────────────────┐
                   │     S3 Landing      │
                   │     CSV / JSON      │
                   └──────────┬──────────┘
                              │
                       Data Profiling
                              │
                              ▼
                        AWS Glue
                         PySpark
                              │
                              ▼
                   ┌─────────────────────┐
                   │       Bronze        │
                   │                     │
                   │ Apache Iceberg v2   │
                   │      Parquet        │
                   └──────────┬──────────┘
                              │
                       Clean / Validate
                              │
                              ▼
                   ┌─────────────────────┐
                   │       Silver        │
                   │                     │
                   │ Apache Iceberg      │
                   └──────────┬──────────┘
                              │
                         Aggregate
                              │
                              ▼
                   ┌─────────────────────┐
                   │        Gold         │
                   │                     │
                   │ Analytics Models    │
                   └──────────┬──────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
                ▼                            ▼
          Amazon Athena                 BI / Analytics
                │
                ▼
       Reporting / Fraud Analysis
```

---

# 31. What This Project Demonstrates

FinGuard demonstrates the progressive development of a cloud Data Engineering platform rather than simply uploading files to S3.

The project covers the data lifecycle:

```text
External Dataset
       ↓
Data Ingestion
       ↓
Cloud Object Storage
       ↓
Data Profiling
       ↓
Distributed Processing
       ↓
Schema Enforcement
       ↓
Data Lineage
       ↓
Apache Iceberg
       ↓
Data Catalog
       ↓
Data Quality
       ↓
Transformation
       ↓
Analytics
       ↓
Monitoring
```

The goal is to progressively evolve the pipeline into a **reusable, scalable, observable and production-style AWS Data Engineering platform**.
