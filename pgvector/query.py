"""
Find the 3 most similar purchases to a given purchase using cosine similarity in pgvector.
"""
import psycopg2

DB_PARAMS = {
    "dbname":   "shop_analytics",
    "user":     "shop_user",
    "password": "shop123",
    "host":     "localhost",
}

REFERENCE_PURCHASE_ID = 1  # find 3 nearest to purchase #1


def main():
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        # Get reference embedding
        cur.execute(
            "SELECT customer_info, embedding FROM purchase_vectors WHERE purchase_id = %s",
            (REFERENCE_PURCHASE_ID,)
        )
        row = cur.fetchone()
        if not row:
            print(f"Purchase {REFERENCE_PURCHASE_ID} not found in DB.")
            return
        ref_customer, ref_embedding = row

        print(f"\n=== Pgvector: 3 nearest purchases to #{REFERENCE_PURCHASE_ID} ===")
        print(f"  Reference: {ref_customer}\n")

        # Find 3 nearest (excluding self)
        cur.execute(
            """
            SELECT purchase_id, customer_info,
                   embedding <=> %s::vector AS distance
            FROM purchase_vectors
            WHERE purchase_id != %s
            ORDER BY distance
            LIMIT 3
            """,
            (str(ref_embedding), REFERENCE_PURCHASE_ID)
        )
        results = cur.fetchall()
        for i, (pid, customer, dist) in enumerate(results, 1):
            print(f"  #{i}: purchase_id={pid}, distance={dist:.6f}")
            print(f"       {customer}")

    conn.close()
    return results


if __name__ == "__main__":
    main()
