"""
pyspark_transform.py
---------------------
Re-implements two of the analyses from queries.sql using PySpark's
DataFrame API instead of raw SQL, reading directly from the CSVs
(not the SQLite database -- Spark works on files/distributed data,
that's the whole point of it).

This runs 100% locally -- no cluster, no cloud, no AWS account
needed. It's the same PySpark DataFrame API used in real production
Spark jobs, just running on your laptop instead of a cluster.

Run with:
    python pyspark_transform.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("CreditRiskPipeline") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")  # quiet the noisy startup logs

# ---------------------------------------------------------
# 1) Load the raw CSVs as Spark DataFrames
# ---------------------------------------------------------
customers = spark.read.csv("data/customers.csv", header=True, inferSchema=True)
loans = spark.read.csv("data/loans.csv", header=True, inferSchema=True)
repayments = spark.read.csv("data/repayments.csv", header=True, inferSchema=True)

print("Schemas loaded by Spark:")
loans.printSchema()

# ---------------------------------------------------------
# 2) Default rate by region
#    (same logic as query #3 in queries.sql, but as a
#    DataFrame transformation pipeline instead of SQL)
# ---------------------------------------------------------
joined = loans.join(customers, on="customer_id", how="inner")

default_rate_by_region = (
    joined.groupBy("region")
    .agg(
        F.count("*").alias("total_loans"),
        F.sum(F.when(F.col("loan_status") == "Default", 1).otherwise(0)).alias("defaults"),
    )
    .withColumn(
        "default_rate_pct",
        F.round(100.0 * F.col("defaults") / F.col("total_loans"), 2),
    )
    .orderBy(F.col("default_rate_pct").desc())
)

print("\n=== Default rate by region (PySpark) ===")
default_rate_by_region.show()

# ---------------------------------------------------------
# 3) Rank customers by total borrowed amount within region
#    (same logic as query #5, using Spark's Window function
#    API -- this is the part worth rehearsing for interviews:
#    Window.partitionBy().orderBy() is Spark's equivalent of
#    SQL's PARTITION BY / ORDER BY)
# ---------------------------------------------------------
total_borrowed = joined.groupBy("region", "customer_id", "name").agg(
    F.sum("loan_amount").alias("total_borrowed")
)

region_window = Window.partitionBy("region").orderBy(F.col("total_borrowed").desc())

ranked = total_borrowed.withColumn("rank_in_region", F.rank().over(region_window))

print("\n=== Top borrowers by region (PySpark window function) ===")
ranked.orderBy("region", "rank_in_region").show(20)

# ---------------------------------------------------------
# 4) Save the result back out (the "output" step of the pipeline)
# ---------------------------------------------------------
default_rate_by_region.toPandas().to_csv("data/output_default_rate_by_region.csv", index=False)

print("\nSaved default_rate_by_region result to data/output_default_rate_by_region.csv")
spark.stop()
