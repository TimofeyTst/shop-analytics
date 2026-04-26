"""
Vectorize purchase documents using OpenAI text-embedding-3-small,
store embeddings in PostgreSQL + pgvector.

Requires: OPENAI_API_KEY environment variable.
"""
import json
import os
import time
import psycopg2
from openai import OpenAI

DB_PARAMS = {
    "dbname":   "shop_analytics",
    "user":     "shop_user",
    "password": "shop123",
    "host":     "localhost",
}

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100

DATA_FILE = "data/purchases.json"


def load_purchases():
    with open(DATA_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def make_text(doc):
    """Concatenate purchase fields into a text for embedding."""
    return (
        f"{doc['customer_info']} "
        f"{doc['product_name']} "
        f"количество {doc['quantity']} "
        f"стоимость {doc['total_price']}"
    )


def embed_batch(client, texts):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_vectors (
                purchase_id   INTEGER PRIMARY KEY,
                customer_info TEXT,
                embedding     vector(1536)
            )
        """)
        cur.execute("TRUNCATE TABLE purchase_vectors")
    conn.commit()
    print("Table purchase_vectors ready.")


def insert_batch(conn, rows):
    with conn.cursor() as cur:
        for purchase_id, customer_info, embedding in rows:
            cur.execute(
                "INSERT INTO purchase_vectors (purchase_id, customer_info, embedding) "
                "VALUES (%s, %s, %s)",
                (purchase_id, customer_info, str(embedding))
            )
    conn.commit()


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)
    purchases = load_purchases()
    print(f"Loaded {len(purchases)} purchases.")

    conn = psycopg2.connect(**DB_PARAMS)
    create_table(conn)

    total = len(purchases)
    for start in range(0, total, BATCH_SIZE):
        batch = purchases[start:start + BATCH_SIZE]
        texts = [make_text(doc) for doc in batch]
        embeddings = embed_batch(client, texts)

        rows = [
            (doc["purchase_id"], doc["customer_info"], emb)
            for doc, emb in zip(batch, embeddings)
        ]
        insert_batch(conn, rows)

        done = min(start + BATCH_SIZE, total)
        print(f"  Embedded and stored {done}/{total} ...")
        time.sleep(0.5)  # gentle rate limiting

    conn.close()
    print("Done. All embeddings stored.")


if __name__ == "__main__":
    main()
