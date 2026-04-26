"""
Find the 3 most similar purchases to a given purchase using cosine distance in pgvector.
Shows the full embedded text for both reference and results so similarity is interpretable.
"""
import psycopg2

DB_PARAMS = {
    "dbname":   "shop_analytics",
    "user":     "shop_user",
    "password": "shop123",
    "host":     "localhost",
}

REFERENCE_PURCHASE_ID = 1


def main():
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT customer_info, embedded_text, embedding "
            "FROM purchase_vectors WHERE purchase_id = %s",
            (REFERENCE_PURCHASE_ID,)
        )
        row = cur.fetchone()
        if not row:
            print(f"Purchase #{REFERENCE_PURCHASE_ID} not found.")
            return

        ref_customer, ref_text, ref_embedding = row

        print(f"=== Reference purchase #{REFERENCE_PURCHASE_ID} ===")
        print(f"  Text sent to model:")
        print(f"  → {ref_text}")

        cur.execute(
            """
            SELECT purchase_id, customer_info, embedded_text,
                   embedding <=> %s::vector AS distance
            FROM purchase_vectors
            WHERE purchase_id != %s
            ORDER BY distance
            LIMIT 3
            """,
            (str(ref_embedding), REFERENCE_PURCHASE_ID)
        )
        results = cur.fetchall()

        print(f"\n=== 3 nearest purchases (cosine distance) ===")
        for i, (pid, customer, text, dist) in enumerate(results, 1):
            print(f"\n  #{i}  purchase_id={pid}  distance={dist:.6f}")
            print(f"       → {text}")

    conn.close()
    return results


if __name__ == "__main__":
    main()
