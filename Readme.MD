# FinGuard — AWS Financial Markets Data Engineering Pipeline

FinGuard is an end-to-end Data Engineering project that ingests financial market data from Kaggle into an AWS-based data lake.

The project demonstrates how raw external datasets can be ingested, organized, validated, transformed, and prepared for analytics using modern Data Engineering practices.

The pipeline follows a layered data architecture:

```text
Kaggle
   │
   │ Python ingestion
   ▼
Amazon S3
   │
   ├── Landing
   │
   ▼
Bronze
   │
   ▼
Silver
   │
   ▼
Gold
   │
   ▼
Analytics / Reporting
```

The current implementation focuses on the **Kaggle → S3 Landing Layer** ingestion process. The project will progressively introduce data validation, Apache Iceberg, transformation, orchestration, data quality, and analytical layers.

---

# 1. Project Objectives

The main objective of FinGuard is to build a realistic cloud Data Engineering pipeline around financial datasets.

The project is designed to demonstrate:

* Python-based data ingestion
* Kaggle dataset integration
* AWS S3 data lake design
* Configuration-driven ingestion
* Date-partitioned data storage
* Reusable Python components
* Schema validation using Pydantic
* Data processing using Pandas
* Apache Iceberg table formats
* Medallion architecture
* Data quality validation
* Pipeline orchestration
* Cloud-native Data Engineering practices

The architecture is intentionally designed so that the ingestion framework can support multiple datasets rather than being tightly coupled to a single CSV file.

---

# 2. Dataset

The current dataset is:

```text
belbino/global-financial-markets-dataset-2010-present
```

It is downloaded programmatically using the Kaggle dataset API/client.

The primary source file currently ingested is:

```text
global_financial_markets_2000_Now.csv
```

The ingestion logic is configuration-driven, allowing additional files or completely different Kaggle datasets to be introduced without rewriting the core ingestion logic.

For example:

```python
file_mappings = {
    "global_financial_markets_2000_Now.csv":
        "landing/global_financial_markets_2000_Now"
}
```

The mapping defines:

```text
Source filename → S3 destination prefix
```

This separates dataset-specific configuration from the reusable ingestion code.

---

# 3. High-Level Architecture

```text
                 ┌─────────────────────┐
                 │       Kaggle        │
                 │  Financial Dataset  │
                 └──────────┬──────────┘
                            │
                            │ Download
                            ▼
                 ┌─────────────────────┐
                 │  Python Ingestion   │
                 │      Pipeline       │
                 │                     │
                 │ • Download dataset  │
                 │ • Discover files    │
                 │ • Build S3 keys     │
                 │ • Upload files      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      Amazon S3      │
                 │    Landing Layer    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Bronze        │
                 │    Apache Iceberg   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Silver        │
                 │ Clean / Validated   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │        Gold         │
                 │ Analytics Models    │
                 └─────────────────────┘
```

---

# 4. Data Lake Architecture

FinGuard follows a Medallion-style architecture consisting of Landing, Bronze, Silver, and Gold layers.

## Landing Layer

The Landing layer contains the original files received from the source system.

Example:

```text
s3://finguard-data/
└── landing/
    └── global_financial_markets_2000_Now/
        └── ingestion_date=2026-09-14/
            └── global_financial_markets_2000_Now.csv
```

The source data is preserved without business transformations.

Keeping the raw source data provides several advantages:

* Source traceability
* Pipeline replay capability
* Easier debugging
* Historical auditing
* Recovery from downstream processing failures

The ingestion date is included in the S3 object key:

```text
ingestion_date=YYYY-MM-DD
```

This provides a logical partitioning structure and makes it possible to identify when a particular dataset was ingested.

---

## Bronze Layer

The Bronze layer represents the structured raw dataset.

The planned implementation will convert source CSV/JSON files into **Apache Iceberg tables backed by Parquet files**.

Conceptually:

```text
Landing CSV
     │
     ▼
Schema validation
     │
     ▼
Data type conversion
     │
     ▼
Apache Iceberg Bronze Table
     │
     ▼
Parquet data files in S3
```

The Bronze layer will retain the source data with minimal transformation while introducing:

* Explicit schemas
* Correct data types
* Standardized column names
* Ingestion metadata
* Apache Iceberg table metadata

Possible metadata columns include:

```text
ingestion_date
source_file
ingestion_timestamp
```

---

## Silver Layer

The Silver layer will contain cleaned and validated financial market data.

Typical processing may include:

* Null handling
* Duplicate removal
* Data type validation
* Date normalization
* Numeric validation
* Invalid-record handling
* Standardized asset and market identifiers
* Data quality checks

For example:

```text
Bronze
   │
   ├── Remove duplicates
   ├── Validate required fields
   ├── Normalize dates
   ├── Validate numeric values
   └── Apply quality rules
          │
          ▼
       Silver
```

Pydantic can be used where appropriate for record/schema validation, while Pandas or a distributed processing engine can perform dataset-level transformations.

---

## Gold Layer

The Gold layer will contain analytics-ready datasets.

Instead of exposing raw financial records directly to reporting applications, the Gold layer can contain business-oriented aggregations.

Examples could include:

```text
daily_market_summary
monthly_asset_performance
market_volatility_summary
asset_class_performance
country_market_performance
```

These datasets can then be consumed by:

* SQL analytics
* BI dashboards
* Financial reporting
* Machine learning pipelines
* Risk analytics

---

# 5. Current Ingestion Workflow

The current Python ingestion pipeline performs the following steps.

## Step 1 — Download Dataset

The configured Kaggle dataset is downloaded:

```python
dataset_path = download_dataset(DATASET_HANDLE)
```

The function returns the local directory containing the downloaded dataset.

---

## Step 2 — Configure Source Files

Files that should be ingested are configured using a mapping:

```python
file_mappings = {
    "global_financial_markets_2000_Now.csv":
        "landing/global_financial_markets_2000_Now"
}
```

This allows the ingestion framework to remain generic.

A future dataset could therefore use:

```python
file_mappings = {
    "transactions.csv": "landing/transactions",
    "customers.csv": "landing/customers"
}
```

without changing the ingestion implementation.

---

## Step 3 — Discover Files

The pipeline discovers the configured files within the downloaded dataset:

```python
dataset_files = discover_files(
    dataset_path,
    file_mappings
)
```

Each discovered file is represented as a `DatasetFile`.

For example:

```python
@dataclass
class DatasetFile:
    file_path: Path
    s3_prefix: str
```

Using a dataclass provides a structured representation of the file metadata passed between pipeline components.

---

## Step 4 — Build the S3 Object Key

The pipeline generates an S3 object key for each source file.

Example:

```text
landing/
global_financial_markets_2000_Now/
ingestion_date=2026-09-14/
global_financial_markets_2000_Now.csv
```

Combined:

```text
landing/global_financial_markets_2000_Now/
ingestion_date=2026-09-14/
global_financial_markets_2000_Now.csv
```

This gives the final S3 URI:

```text
s3://finguard-data/landing/global_financial_markets_2000_Now/
ingestion_date=2026-09-14/
global_financial_markets_2000_Now.csv
```

---

## Step 5 — Upload to Amazon S3

Each discovered file is uploaded using:

```python
upload_file(
    dataset_file=dataset_file,
    bucket_name=BUCKET_NAME
)
```

AWS authentication is handled through the AWS SDK credential provider chain rather than storing credentials directly in the Python source code.

Credentials should **never be hardcoded or committed to Git**.

---

# 6. Project Structure

A scalable project structure could look like:

```text
FinGuard_AWS_Project/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── src/
│   └── finguard/
│       │
│       ├── __init__.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── kaggle_client.py
│       │   ├── file_discovery.py
│       │   └── s3_uploader.py
│       │
│       ├── models/
│       │   └── dataset_file.py
│       │
│       ├── validation/
│       │   └── schemas.py
│       │
│       └── transformations/
│           ├── bronze.py
│           ├── silver.py
│           └── gold.py
│
├── scripts/
│   └── ingest.py
│
├── tests/
│   ├── test_file_discovery.py
│   ├── test_s3_key.py
│   └── test_validation.py
│
└── config/
    └── datasets.yaml
```

As the project grows, dataset-specific configuration can be moved from Python into YAML.

For example:

```yaml
dataset:
  name: global_financial_markets
  kaggle_handle: belbino/global-financial-markets-dataset-2010-present

files:
  global_financial_markets_2000_Now.csv:
    s3_prefix: landing/global_financial_markets_2000_Now
```

This would make the ingestion pipeline completely configuration-driven.

---

# 7. Technology Stack

| Technology     | Purpose                                  |
| -------------- | ---------------------------------------- |
| Python         | Data ingestion and processing            |
| uv             | Python dependency/environment management |
| Kaggle         | External dataset source                  |
| Pandas         | Data analysis and transformations        |
| Pydantic       | Schema and field validation              |
| AWS S3         | Data lake storage                        |
| boto3          | AWS SDK / S3 interaction                 |
| Apache Parquet | Columnar storage format                  |
| Apache Iceberg | Data lake table format                   |
| Git            | Source control                           |

Future components may include:

```text
AWS Glue
Amazon Athena
Apache Airflow
PySpark
AWS Lambda
CloudWatch
GitHub Actions
```

---

# 8. Running the Project

## Prerequisites

The following are required:

```text
Python
uv
AWS account
AWS CLI
Kaggle access
```

AWS credentials must be configured before running the ingestion process.

Verify the current AWS identity using:

```bash
aws sts get-caller-identity
```

Verify the configured region:

```bash
aws configure get region
```

---

## Install Dependencies

Using `uv`:

```bash
uv sync
```

or when adding dependencies:

```bash
uv add boto3 pandas pydantic kagglehub
```

---

## Run the Ingestion Pipeline

From the project root:

```bash
uv run python scripts/ingest.py
```

The pipeline should:

```text
1. Download the Kaggle dataset
2. Discover configured files
3. Generate S3 object keys
4. Upload the files to S3
```

Example console output:

```text
File: global_financial_markets_2000_Now.csv

S3 destination:
landing/global_financial_markets_2000_Now

S3 key:
landing/global_financial_markets_2000_Now/
ingestion_date=2026-09-14/
global_financial_markets_2000_Now.csv
```

---

# 9. Design Decisions

## Why keep a Landing layer?

The Landing layer preserves the source data before transformations are applied.

This makes the pipeline replayable and provides traceability between the original source and downstream datasets.

---

## Why partition by ingestion date?

Using:

```text
ingestion_date=YYYY-MM-DD
```

allows individual ingestion runs to be logically separated.

It also supports:

* Incremental processing
* Historical investigation
* Pipeline replay
* Auditing
* Partition pruning in downstream systems where applicable

---

## Why use configuration-driven file mappings?

Hardcoding dataset-specific behaviour inside ingestion functions makes pipelines difficult to reuse.

Instead:

```python
filename → destination
```

is treated as configuration.

The same ingestion engine can therefore support different datasets.

---

## Why Apache Iceberg?

Simply storing Parquet files in S3 provides efficient columnar storage, but does not by itself provide database-like table management.

Apache Iceberg adds capabilities such as:

* Schema evolution
* Partition evolution
* ACID transactions
* Snapshot management
* Time travel
* Reliable table metadata
* Better management of large analytical datasets

Therefore the planned Bronze/Silver/Gold layers will use Iceberg rather than treating S3 as only a collection of Parquet files.

---

# 10. Data Quality Strategy

Data quality validation will be introduced before records progress into curated layers.

Example rules:

```text
Required fields must not be null
Dates must use valid formats
Prices must be numeric
Volumes must not be negative
Duplicate records should be identified
Unexpected schema changes should be detected
```

Pydantic can validate selected record-level fields:

```python
class MarketRecord(BaseModel):
    symbol: str
    price: float
    volume: int
```

Pandas can perform dataset-level checks such as:

```text
null counts
duplicate detection
source/target comparison
statistical validation
```

Invalid records may eventually be written to a quarantine location:

```text
s3://finguard-data/quarantine/
```

rather than silently discarded.

---

# 11. Planned Architecture

The target architecture is:

```text
                         Kaggle
                            │
                            ▼
                    Python Ingestion
                            │
                            ▼
                 ┌──────────────────┐
                 │    S3 Landing    │
                 │   CSV / JSON     │
                 └────────┬─────────┘
                          │
                    Validation
                          │
                          ▼
                 ┌──────────────────┐
                 │      Bronze      │
                 │ Iceberg/Parquet  │
                 └────────┬─────────┘
                          │
                  Clean + Validate
                          │
                          ▼
                 ┌──────────────────┐
                 │      Silver      │
                 │ Iceberg/Parquet  │
                 └────────┬─────────┘
                          │
                    Aggregate
                          │
                          ▼
                 ┌──────────────────┐
                 │       Gold       │
                 │ Analytics-ready  │
                 └────────┬─────────┘
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
           Athena                 BI / Analytics
```

---

# 12. Future Enhancements

The project will be extended incrementally with:

* [x] Kaggle dataset download
* [x] Generic file discovery
* [x] Configuration-based S3 destinations
* [x] S3 Landing layer
* [x] Date-partitioned ingestion
* [ ] Pydantic schema validation
* [ ] Parquet conversion
* [ ] Apache Iceberg Bronze tables
* [ ] Silver data cleaning
* [ ] Gold analytical models
* [ ] AWS Glue Data Catalog
* [ ] Amazon Athena querying
* [ ] Apache Airflow orchestration
* [ ] Automated data quality checks
* [ ] Unit tests
* [ ] Integration tests
* [ ] CI/CD pipeline
* [ ] CloudWatch monitoring and alerting
* [ ] Infrastructure as Code

---

# 13. Engineering Principles

The project aims to follow several production Data Engineering principles:

**Separation of concerns**

Dataset download, file discovery, S3 key generation, upload, validation, and transformation are implemented as separate responsibilities.

**Configuration over hardcoding**

Dataset-specific configuration is separated from reusable pipeline logic.

**Raw data preservation**

Original source data is retained in the Landing layer.

**Idempotency**

Future versions of the pipeline will ensure rerunning an ingestion process does not unintentionally duplicate or corrupt data.

**Observability**

Structured logging, metrics, and pipeline monitoring will be introduced as the project evolves.

**Testability**

Core functions such as file discovery, S3 key generation, schema validation, and transformations are designed to be independently testable.

---

# 14. What This Project Demonstrates

FinGuard is intended to demonstrate practical experience with the complete lifecycle of a modern cloud Data Engineering pipeline:

```text
Source ingestion
       ↓
Cloud storage
       ↓
Data modelling
       ↓
Schema validation
       ↓
Data quality
       ↓
Table formats
       ↓
Transformation
       ↓
Orchestration
       ↓
Analytics
       ↓
Monitoring
```

Rather than focusing only on moving a CSV file into S3, the project progressively develops the ingestion process into a reusable, observable, testable, and production-style Data Engineering platform.
