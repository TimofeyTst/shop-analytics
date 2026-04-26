"""Bulk-index purchases and products into Elasticsearch."""
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch("http://localhost:9200")


def load_ndjson(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def make_actions(docs, index_name, id_field):
    for doc in docs:
        yield {
            "_index": index_name,
            "_id":    doc[id_field],
            "_source": doc,
        }


purchases = load_ndjson("data/purchases.json")
products  = load_ndjson("data/products.json")

for index_name, docs, id_field in [
    ("purchases", purchases, "purchase_id"),
    ("products",  products,  "product_id"),
]:
    success, errors = bulk(es, make_actions(docs, index_name, id_field), chunk_size=500)
    print(f"{index_name}: indexed {success} docs, {len(errors)} errors")

print("Done.")
