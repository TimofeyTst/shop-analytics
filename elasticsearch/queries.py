"""
Elasticsearch aggregation queries for the online shop analytics.

Query 1: Products grouped by batch_date (monthly) with sold quantity per product name.
Query 2: Total revenue from products with batch_date in the last 2 months of the dataset
         (Nov-Dec 2024, since data spans 2023-01-01 to 2024-12-31).
"""
import json
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Reference date: end of our dataset (2024-12-31)
# "Last 2 months" = 2024-11-01 to 2024-12-31
PERIOD_FROM = "2024-11-01"
PERIOD_TO   = "2024-12-31"


def run_query1():
    """Monthly breakdown of products with sold quantity per product name (nested agg)."""
    body = {
        "size": 0,
        "aggs": {
            "by_month": {
                "date_histogram": {
                    "field": "batch_date",
                    "calendar_interval": "month",
                    "format": "yyyy-MM"
                },
                "aggs": {
                    "by_product": {
                        "terms": {
                            "field": "product_name",
                            "size": 30
                        },
                        "aggs": {
                            "total_sold": {
                                "sum": {"field": "sold_quantity"}
                            }
                        }
                    }
                }
            }
        }
    }
    result = es.search(index="products", body=body)
    print("\n=== Query 1: Products by month with sold quantity per product name ===")
    buckets = result["aggregations"]["by_month"]["buckets"]
    print(f"Total months in dataset: {len(buckets)}")
    for month_bucket in buckets[:3]:
        month = month_bucket["key_as_string"]
        products = month_bucket["by_product"]["buckets"]
        print(f"\n  Month: {month} ({month_bucket['doc_count']} products)")
        for p in products[:5]:
            print(f"    {p['key']}: {int(p['total_sold']['value'])} sold")
    print("  ... (showing first 3 months)")
    return result


def run_query2():
    """Total revenue (sold_quantity * unit_price) for the last 2 months of the dataset."""
    body = {
        "size": 0,
        "query": {
            "range": {
                "batch_date": {
                    "gte": PERIOD_FROM,
                    "lte": PERIOD_TO
                }
            }
        },
        "aggs": {
            "total_revenue": {
                "sum": {
                    "script": {
                        "source": "doc['sold_quantity'].value * doc['unit_price'].value"
                    }
                }
            },
            "product_count": {
                "value_count": {"field": "product_id"}
            }
        }
    }
    result = es.search(index="products", body=body)
    revenue = result["aggregations"]["total_revenue"]["value"]
    count   = result["aggregations"]["product_count"]["value"]
    print(f"\n=== Query 2: Total revenue for {PERIOD_FROM} – {PERIOD_TO} (last 2 months) ===")
    print(f"  Products in period: {count}")
    print(f"  Total revenue: {revenue:,.2f} RUB")
    return result


if __name__ == "__main__":
    r1 = run_query1()
    r2 = run_query2()

    print("\nSaving results to elasticsearch/query_results.json ...")
    with open("elasticsearch/query_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "query1_monthly_sales": r1["aggregations"],
            "query2_total_revenue": r2["aggregations"],
            "query2_period": {"from": PERIOD_FROM, "to": PERIOD_TO},
        }, f, ensure_ascii=False, indent=2)
    print("Done.")
