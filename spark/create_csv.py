"""
Читает данные покупок и товаров из Elasticsearch,
создаёт три таблицы и сохраняет их как CSV в HDFS.

Таблицы:
  - customers  (customer_id, customer_info) — уникальные покупатели
  - purchases  (purchase_id, customer_id, purchase_date, product_id, quantity, total_price)
  - products   (product_id, product_name, unit_price) — уникальные товары
"""
import sys
import os

# elasticsearch-py должен быть доступен — добавляем путь к venv
sys.path.insert(0, "/home/timofeytst/shop-analytics/venv/lib/python3.12/site-packages")

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, FloatType
)

ES_HOST  = "http://localhost:9200"
HDFS_BASE = "hdfs://localhost:9000/shop-analytics"


def fetch_from_es(index: str) -> list[dict]:
    """Получает все документы из указанного индекса через scroll API."""
    es   = Elasticsearch(ES_HOST)
    hits = scan(es, index=index, query={"query": {"match_all": {}}})
    docs = [hit["_source"] for hit in hits]
    print(f"Получено из ES [{index}]: {len(docs)} документов")
    return docs


def main():
    spark = SparkSession.builder         .appName("ShopAnalytics-CreateCSV")         .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # --- Получаем данные из Elasticsearch ---
    purchases_raw = fetch_from_es("purchases")
    products_raw  = fetch_from_es("products")

    # --- Схема для покупок ---
    purchases_schema = StructType([
        StructField("purchase_id",   IntegerType(), True),
        StructField("customer_id",   IntegerType(), True),
        StructField("customer_info",  StringType(),  True),
        StructField("purchase_date",  StringType(),  True),
        StructField("product_id",    IntegerType(), True),
        StructField("product_name",  StringType(),  True),
        StructField("quantity",      IntegerType(), True),
        StructField("total_price",   FloatType(),   True),
    ])

    # --- Схема для товаров ---
    products_schema = StructType([
        StructField("product_id",       IntegerType(), True),
        StructField("product_name",     StringType(),  True),
        StructField("batch_date",       StringType(),  True),
        StructField("stock_quantity",   IntegerType(), True),
        StructField("sold_quantity",    IntegerType(), True),
        StructField("unit_price",       FloatType(),   True),
        StructField("description",      StringType(),  True),
        StructField("image_url",        StringType(),  True),
    ])

    purchases_df = spark.createDataFrame(purchases_raw, schema=purchases_schema)
    products_df  = spark.createDataFrame(products_raw,  schema=products_schema)

    print(f"Purchases: {purchases_df.count()} строк")
    print(f"Products:  {products_df.count()} строк")

    # --- Таблица customers (уникальные по customer_id) ---
    customers_df = purchases_df         .select("customer_id", "customer_info")         .dropDuplicates(["customer_id"])         .orderBy("customer_id")
    print(f"Уникальных покупателей: {customers_df.count()}")

    # --- Таблица purchases ---
    purchases_clean = purchases_df.select(
        "purchase_id", "customer_id", "purchase_date",
        "product_id", "quantity", "total_price"
    )

    # --- Таблица products (уникальные по product_id) ---
    products_clean = products_df.select(
        "product_id", "product_name", "unit_price"
    ).dropDuplicates(["product_id"]).orderBy("product_id")
    print(f"Уникальных товаров: {products_clean.count()}")

    # --- Сохраняем в HDFS ---
    for df, name in [
        (customers_df,    "customers"),
        (purchases_clean, "purchases"),
        (products_clean,  "products"),
    ]:
        path = f"{HDFS_BASE}/{name}"
        df.coalesce(1).write.csv(path, header=True, mode="overwrite")
        print(f"Сохранено: {name} → {path}")

    print("\nГотово.")
    spark.stop()


if __name__ == "__main__":
    main()
