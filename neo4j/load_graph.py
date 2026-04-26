"""
Загрузка данных из Elasticsearch в Neo4j.

Читает покупки из индекса ES 'purchases' (не из файлов),
строит граф:
  (Purchase {purchase_id, purchase_date, customer_info})
    -[:INCLUDES {quantity, total_price}]->
  (Product {product_id, product_name})
"""
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from neo4j import GraphDatabase

ES_URL   = "http://localhost:9200"
BOLT_URI = "bolt://localhost:7687"
AUTH     = ("neo4j", "neo4j123")


def fetch_purchases_from_es() -> list[dict]:
    """Получает все документы из индекса purchases через scroll API."""
    es   = Elasticsearch(ES_URL)
    hits = scan(es, index="purchases", query={"query": {"match_all": {}}})
    docs = [hit["_source"] for hit in hits]
    print(f"Получено из Elasticsearch: {len(docs)} покупок")
    return docs


def clear_graph(session) -> None:
    session.run("MATCH (n) DETACH DELETE n")
    print("Граф очищен.")


def load_into_graph(session, purchases: list[dict]) -> None:
    """Создаёт узлы Purchase и Product, связывает их отношением INCLUDES."""
    query = """
    MERGE (purchase:Purchase {purchase_id: $purchase_id})
      ON CREATE SET
        purchase.purchase_date = $purchase_date,
        purchase.customer_info = $customer_info
    MERGE (product:Product {product_id: $product_id})
      ON CREATE SET
        product.product_name = $product_name
    MERGE (purchase)-[r:INCLUDES]->(product)
      ON CREATE SET
        r.quantity    = $quantity,
        r.total_price = $total_price
    """
    for i, doc in enumerate(purchases):
        session.run(
            query,
            purchase_id  = doc["purchase_id"],
            purchase_date= doc["purchase_date"],
            customer_info= doc["customer_info"],
            product_id   = doc["product_id"],
            product_name = doc["product_name"],
            quantity     = doc["quantity"],
            total_price  = doc["total_price"],
        )
        if (i + 1) % 200 == 0:
            print(f"  Загружено {i + 1} / {len(purchases)} ...")
    print(f"Граф заполнен: {len(purchases)} покупок.")


def main():
    purchases = fetch_purchases_from_es()

    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    with driver.session() as session:
        clear_graph(session)
        load_into_graph(session, purchases)
    driver.close()
    print("Готово.")


if __name__ == "__main__":
    main()
