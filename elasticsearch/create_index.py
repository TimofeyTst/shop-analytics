"""Create Elasticsearch indices with Russian analyzer and field mappings."""
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

RUSSIAN_SETTINGS = {
    "analysis": {
        "filter": {
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_" # встроенный список Elasticsearch (~150 слов: предлоги, союзы, местоимения: "и", "в")
            }
        },
        "analyzer": {
            "russian_custom": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "russian_stop"]
            }
        }
    }
}

PURCHASES_MAPPING = {
    "properties": {
        "purchase_id":   {"type": "integer"},
        "customer_id":   {"type": "integer"},
        "customer_info": {"type": "text", "analyzer": "russian_custom"},
        "purchase_date": {"type": "date", "format": "yyyy-MM-dd"},
        "product_id":    {"type": "integer"},
        "product_name":  {"type": "keyword"},
        "quantity":      {"type": "integer"},
        "total_price":   {"type": "float"},
    }
}

PRODUCTS_MAPPING = {
    "properties": {
        "product_id":     {"type": "integer"},
        "product_name":   {"type": "keyword"},
        "batch_date":     {"type": "date", "format": "yyyy-MM-dd"},
        "stock_quantity": {"type": "integer"},
        "sold_quantity":  {"type": "integer"},
        "unit_price":     {"type": "float"},
        "description":    {"type": "text", "analyzer": "russian_custom"},
        "image_url":      {"type": "keyword"},
    }
}

for index_name, mapping in [("purchases", PURCHASES_MAPPING), ("products", PRODUCTS_MAPPING)]:
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Deleted existing index: {index_name}")

    es.indices.create(
        index=index_name,
        body={"settings": RUSSIAN_SETTINGS, "mappings": mapping}
    )
    print(f"Created index: {index_name}")

print("Done.")
