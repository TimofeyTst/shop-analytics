"""
Neo4j Cypher query: find the customer who paid the most across all purchases.
"""
from neo4j import GraphDatabase

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "neo4j123")

QUERY = """
MATCH (p:Purchase)-[r:INCLUDES]->(t:Product)
WITH p.customer_info AS customer, sum(r.total_price) AS total_spent
ORDER BY total_spent DESC
LIMIT 1
RETURN customer, total_spent
"""


def main():
    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    with driver.session() as session:
        result = session.run(QUERY)
        record = result.single()
        customer    = record["customer"]
        total_spent = record["total_spent"]
        print("\n=== Neo4j Query: Customer with highest total spend ===")
        print(f"  Customer:    {customer}")
        print(f"  Total spent: {total_spent:,.2f} RUB")
    driver.close()
    return customer, total_spent


if __name__ == "__main__":
    main()
