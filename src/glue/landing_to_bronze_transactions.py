import sys
from datetime import date


from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    LongType,
    DoubleType,
    StringType,
    TimestampType,
)

from pyspark.sql.functions import (
    current_timestamp,
    input_file_name,
    lit,
    to_date,
    col,
)


# ---------------------------------------------------------
# Job parameters
# ---------------------------------------------------------

args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME"]
)


# ---------------------------------------------------------
# Initialise Glue / Spark
# ---------------------------------------------------------

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# ---------------------------------------------------------
# Today's ingestion date
# ---------------------------------------------------------

ingestion_date = date.today().isoformat()

print(f"INGESTION_DATE: {ingestion_date}")


# ---------------------------------------------------------
# Build today's Landing path
# ---------------------------------------------------------

landing_path = (
    f"s3://finguard-data/landing/transactions_data/"
    f"ingestion_date={ingestion_date}/"
)

print(f"LANDING_PATH: {landing_path}")


# ---------------------------------------------------------
# Explicit transaction schema
# ---------------------------------------------------------

transaction_schema = StructType([
    StructField("id", LongType(), True),
    StructField("date", TimestampType(), True),
    StructField("client_id", LongType(), True),
    StructField("card_id", LongType(), True),
    StructField("amount", StringType(), True),
    StructField("use_chip", StringType(), True),
    StructField("merchant_id", LongType(), True),
    StructField("merchant_city", StringType(), True),
    StructField("merchant_state", StringType(), True),
    StructField("zip", DoubleType(), True),
    StructField("mcc", IntegerType(), True),
    StructField("errors", StringType(), True),
])


# ---------------------------------------------------------
# Read today's Landing partition
# ---------------------------------------------------------

df = (
    spark.read
    .option("header", "true")
    .schema(transaction_schema)
    .csv(landing_path)
)


# ---------------------------------------------------------
# Add Bronze metadata
# ---------------------------------------------------------

bronze_df = (
    df
    .withColumn(
        "ingestion_date",
        to_date(lit(ingestion_date))
    )
    .withColumn(
        "bronze_ingestion_timestamp",
        current_timestamp()
    )
    .withColumn(
        "source_file",
        input_file_name()
    )
)


# ---------------------------------------------------------
# Write Iceberg table
# ---------------------------------------------------------

table_name = "glue_catalog.finguard_bronze.transactions"

(
    bronze_df
    .writeTo(table_name)
    .using("iceberg")
    .partitionedBy(col("ingestion_date"))
    .tableProperty(
        "location",
        "s3://finguard-data/bronze/transactions_data/"
    )
    .tableProperty(
        "format-version",
        "2"
    )
    .create()
)


job.commit()