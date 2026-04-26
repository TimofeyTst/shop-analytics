"""
Read purchase and product JSON data, create three DataFrames,
and save them as CSV files to HDFS.

Tables:
  - customers  (customer_id, customer_info) — unique customers from purchases
  - purchases  (purchase_id, customer_id, purchase_date, product_id, quantity, total_price)
  - products   (product_id, product_name, unit_price) — unique products from products.json
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

HDFS_BASE = "hdfs://localhost:9000/shop-analytics"
DATA_DIR  = "file:///home/timofeytst/shop-analytics/data"

spark = SparkSession.builder \
    .appName("ShopAnalytics-CreateCSV") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- Load raw JSON ---
purchases_df = spark.read.json(f"{DATA_DIR}/purchases.json")
products_df  = spark.read.json(f"{DATA_DIR}/products.json")

print(f"Purchases raw: {purchases_df.count()} rows")
print(f"Products raw:  {products_df.count()} rows")

# --- Build customers table (unique per customer_id) ---
customers_df = purchases_df \
    .select("customer_id", "customer_info") \
    .dropDuplicates(["customer_id"]) \
    .orderBy("customer_id")

print(f"Unique customers: {customers_df.count()}")

# --- Build purchases table ---
purchases_clean = purchases_df.select(
    "purchase_id", "customer_id", "purchase_date",
    "product_id", "quantity", "total_price"
)

# --- Build products table (unique per product_id) ---
products_clean = products_df.select(
    "product_id", "product_name", "unit_price"
).dropDuplicates(["product_id"]).orderBy("product_id")

print(f"Unique products: {products_clean.count()}")

# --- Save to HDFS ---
for df, name in [
    (customers_df,    "customers"),
    (purchases_clean, "purchases"),
    (products_clean,  "products"),
]:
    path = f"{HDFS_BASE}/{name}"
    df.coalesce(1).write.csv(path, header=True, mode="overwrite")
    print(f"Saved {name} → {path}")

print("\nDone. HDFS contents:")
spark.stop()
