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
    conn = database_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO moderation_analytics
                (content_id, decision)
                VALUES (%s, %s)
                ''',
                (
                    event["content_id"],
                    event.get("final_decision", "UNKNOWN"),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    print(
        f"[analytics-service] recorded decision={event.get('final_decision')}",
        flush=True,
    )


if __name__ == "__main__":
    consume_forever("analytics-service", "moderation.completed", handle)
