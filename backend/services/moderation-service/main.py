import json
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


def evaluate(scores):
    maximum = max(scores.values()) if scores else 0

    if maximum >= 0.75:
        return "REMOVE", f"Maximum risk score {maximum} exceeded removal threshold"
    if maximum >= 0.45:
        return "REVIEW", f"Maximum risk score {maximum} requires human review"
    return "ALLOW", f"Maximum risk score {maximum} is below moderation thresholds"


def handle(event, producer):
    decision, reason = evaluate(event.get("scores", {}))
    event["final_decision"] = decision
    event["reason"] = reason
    event["policy_version"] = "policy-v1"

    conn = database_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE content_items
                SET status = 'MODERATED',
                    final_decision = %s,
                    scores = %s::jsonb,
                    reason = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                ''',
                (
                    decision,
                    json.dumps(event.get("scores", {})),
                    reason,
                    event["content_id"],
                ),
            )
            cursor.execute(
                '''
                INSERT INTO moderation_audit
                (content_id, event_type, payload)
                VALUES (%s, %s, %s::jsonb)
                ''',
                (
                    event["content_id"],
                    "MODERATION_COMPLETED",
                    json.dumps(event),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    producer.publish("moderation.completed", "MODERATION_COMPLETED", event)


if __name__ == "__main__":
    consume_forever("moderation-service", "ml.scored", handle)
