"""
Spark SQL query: find the customer and product with the maximum single-purchase price.
Also captures Spark job metrics from the REST API.
"""
import json
import time
import urllib.request
from pyspark.sql import SparkSession

HDFS_BASE = "hdfs://localhost:9000/shop-analytics"

spark = SparkSession.builder \
    .appName("ShopAnalytics-Query") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Load CSVs from HDFS
for name in ("customers", "purchases", "products"):
    df = spark.read.csv(f"{HDFS_BASE}/{name}", header=True, inferSchema=True)
    df.createOrReplaceTempView(name)
    print(f"Loaded view '{name}': {df.count()} rows")

# SQL: customer and product with maximum purchase price
SQL = """
SELECT
    c.customer_info,
    p.product_name,
    pu.total_price
FROM purchases pu
JOIN customers c ON pu.customer_id = c.customer_id
JOIN products  p ON pu.product_id  = p.product_id
ORDER BY pu.total_price DESC
LIMIT 1
"""

print("\n=== Spark SQL: customer + product with max purchase price ===")
result = spark.sql(SQL)
result.show(truncate=False)

row = result.collect()[0]
print(f"Customer:    {row['customer_info']}")
print(f"Product:     {row['product_name']}")
print(f"Total price: {row['total_price']:,.2f} RUB")

# Fetch Spark monitor data from REST API
time.sleep(2)
try:
    url = "http://localhost:4040/api/v1/applications"
    with urllib.request.urlopen(url, timeout=5) as resp:
        apps = json.loads(resp.read())
    app = apps[0]
    app_id = app["id"]

    url2 = f"http://localhost:4040/api/v1/applications/{app_id}/jobs"
    with urllib.request.urlopen(url2, timeout=5) as resp:
        jobs = json.loads(resp.read())

    print(f"\n=== Spark Monitor: {len(jobs)} jobs ===")
    for job in jobs:
        print(f"  Job {job['jobId']}: {job['name']} — status={job['status']}, "
              f"tasks={job.get('numTasks', '?')}, "
              f"duration={job.get('submissionTime', '')} → {job.get('completionTime', '')}")

    monitor_data = {
        "app_id":    app_id,
        "app_name":  app["name"],
        "jobs":      jobs,
    }
    with open("spark/monitor_results.json", "w") as f:
        json.dump(monitor_data, f, indent=2)
    print("Monitor data saved to spark/monitor_results.json")
except Exception as e:
    print(f"Could not fetch monitor data: {e}")

time.sleep(200)

spark.stop()
print("\nDone.")
