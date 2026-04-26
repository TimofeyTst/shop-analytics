"""
Примеры запросов к Neo4j:
1) Клиент с наибольшей суммой покупок.
2) Графовая рекомендация:
   похожие клиенты по пересечению купленных товаров и товары,
   которые они покупали, а целевой клиент еще нет.
"""
from neo4j import GraphDatabase

BOLT_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "neo4j123")

TOP_SPENDER_QUERY = """
MATCH (p:Purchase)-[r:INCLUDES]->(:Product)
WITH p.customer_info AS customer, sum(r.total_price) AS total_spent
ORDER BY total_spent DESC
LIMIT 1
RETURN customer, total_spent
"""

SIMILAR_CUSTOMERS_RECOMMENDATIONS_QUERY = """
MATCH (me_purchase:Purchase {customer_info: $target_customer})-[:INCLUDES]->(my_product:Product)
WITH collect(DISTINCT my_product) AS my_products
MATCH (other_purchase:Purchase)-[:INCLUDES]->(common_product:Product)
WHERE other_purchase.customer_info <> $target_customer
  AND common_product IN my_products
WITH
  my_products,
  other_purchase.customer_info AS similar_customer,
  count(DISTINCT common_product) AS overlap_products_count
ORDER BY overlap_products_count DESC, similar_customer ASC
LIMIT $similar_customers_limit
MATCH (similar_purchase:Purchase {customer_info: similar_customer})-[:INCLUDES]->(recommended:Product)
WHERE NOT recommended IN my_products
RETURN
  similar_customer,
  overlap_products_count,
  collect(DISTINCT recommended.product_name)[0..$recommendations_per_customer] AS recommended_products
ORDER BY overlap_products_count DESC, similar_customer ASC
"""


def run_top_spender(session):
    result = session.run(TOP_SPENDER_QUERY)
    record = result.single()
    if record is None:
        print("\n=== Neo4j Query: Customer with highest total spend ===")
        print("  Нет данных в графе.")
        return None, None

    customer = record["customer"]
    total_spent = record["total_spent"]
    print("\n=== Neo4j Query: Customer with highest total spend ===")
    print(f"  Customer:    {customer}")
    print(f"  Total spent: {total_spent:,.2f} RUB")
    return customer, total_spent


def run_similarity_recommendations(
    session,
    target_customer: str,
    similar_customers_limit: int = 3,
    recommendations_per_customer: int = 5,
):
    result = session.run(
        SIMILAR_CUSTOMERS_RECOMMENDATIONS_QUERY,
        target_customer=target_customer,
        similar_customers_limit=similar_customers_limit,
        recommendations_per_customer=recommendations_per_customer,
    )
    rows = list(result)

    print("\n=== Neo4j Query: Similar customers and recommendations ===")
    print(f"  Target customer: {target_customer}")
    if not rows:
        print("  Не найдены похожие клиенты или рекомендации.")
        return []

    for i, row in enumerate(rows, start=1):
        recommended = row["recommended_products"] or []
        if recommended:
            recommended_str = ", ".join(recommended)
        else:
            recommended_str = "нет новых товаров"
        print(
            f"  {i}. {row['similar_customer']} "
            f"(общих товаров: {row['overlap_products_count']}) -> "
            f"{recommended_str}"
        )
    return rows


def main(
    target_customer: str | None = None,
    similar_customers_limit: int = 3,
    recommendations_per_customer: int = 5,
):
    driver = GraphDatabase.driver(BOLT_URI, auth=AUTH)
    try:
        with driver.session() as session:
            top_customer, top_total = run_top_spender(session)
            customer_for_recommendations = target_customer or top_customer
            if customer_for_recommendations is None:
                print("\n=== Neo4j Query: Similar customers and recommendations ===")
                print("  Нет данных в графе.")
                return top_customer, top_total, []

            related_products = run_similarity_recommendations(
                session=session,
                target_customer=customer_for_recommendations,
                similar_customers_limit=similar_customers_limit,
                recommendations_per_customer=recommendations_per_customer,
            )
        return top_customer, top_total, related_products
    finally:
        driver.close()


if __name__ == "__main__":
    main()
