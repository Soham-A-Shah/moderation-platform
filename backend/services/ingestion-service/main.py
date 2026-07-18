import os

import psycopg2

from moderation_common.events import consume_forever


def database_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "moderation"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )


def handle(event, producer):
    normalized = " ".join(event.get("text", "").lower().split())

    conn = database_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE content_items
                SET normalized_text = %s,
                    status = 'NORMALIZED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                ''',
                (normalized, event["content_id"]),
            )
        conn.commit()
    finally:
        conn.close()

    event["normalized_text"] = normalized
    producer.publish("content.normalized", "CONTENT_NORMALIZED", event)


if __name__ == "__main__":
    consume_forever("ingestion-service", "content.submitted", handle)
