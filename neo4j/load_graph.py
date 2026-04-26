"""
Load purchase data from Elasticsearch into Neo4j graph database.

Graph schema:
  (Purchase {purchase_id, purchase_date, customer_info})
    -[:INCLUDES {quantity, total_price}]->
  (Product {product_id, product_name})
"""
import json
from neo4j import GraphDatabase

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "neo4j123")

DATA_FILE = "data/purchases.json"


def load_purchases():
    with open(DATA_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def clear_graph(session):
    session.run("MATCH (n) DETACH DELETE n")
    print("Graph cleared.")


def create_graph(session, purchases):
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
        session.run(query,
            purchase_id  = doc["purchase_id"],
            purchase_date= doc["purchase_date"],
            customer_info= doc["customer_info"],
            product_id   = doc["product_id"],
            product_name = doc["product_name"],
            quantity     = doc["quantity"],
            total_price  = doc["total_price"],
        )
        if (i + 1) % 200 == 0:
            print(f"  Loaded {i + 1} / {len(purchases)} ...")
    print(f"Graph loaded: {len(purchases)} purchases.")


def main():
    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    purchases = load_purchases()
    with driver.session() as session:
        clear_graph(session)
        create_graph(session, purchases)
    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
