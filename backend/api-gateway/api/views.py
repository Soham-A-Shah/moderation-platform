import json
import uuid

import psycopg2
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from moderation_common.events import EventProducer


def connection():
    config = settings.DATABASES["default"]
    return psycopg2.connect(
        dbname=config["NAME"],
        user=config["USER"],
        password=config["PASSWORD"],
        host=config["HOST"],
        port=config["PORT"],
    )


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "api-gateway"})


class ContentCollectionView(APIView):
    def get(self, request):
        conn = connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT id, user_id, original_text, status, final_decision,
                           scores, reason, created_at, updated_at
                    FROM content_items
                    ORDER BY created_at DESC
                    LIMIT 50
                    '''
                )
                rows = cursor.fetchall()
                return Response(
                    [
                        {
                            "id": str(row[0]),
                            "user_id": row[1],
                            "text": row[2],
                            "status": row[3],
                            "final_decision": row[4],
                            "scores": row[5],
                            "reason": row[6],
                            "created_at": row[7],
                            "updated_at": row[8],
                        }
                        for row in rows
                    ]
                )
        finally:
            conn.close()

    def post(self, request):
        user_id = request.data.get("user_id", "anonymous")
        text = request.data.get("text", "").strip()

        if not text:
            return Response(
                {"detail": "text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_id = str(uuid.uuid4())

        conn = connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO content_items
                    (id, user_id, original_text, status)
                    VALUES (%s, %s, %s, 'SUBMITTED')
                    ''',
                    (content_id, user_id, text),
                )
            conn.commit()
        finally:
            conn.close()

        event = EventProducer().publish(
            "content.submitted",
            "CONTENT_SUBMITTED",
            {
                "content_id": content_id,
                "user_id": user_id,
                "text": text,
            },
        )

        return Response(
            {
                "accepted": True,
                "content_id": content_id,
                "status": "SUBMITTED",
                "event": event,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ContentDetailView(APIView):
    def get(self, request, content_id):
        conn = connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT id, user_id, original_text, normalized_text, status,
                           final_decision, scores, reason, created_at, updated_at
                    FROM content_items
                    WHERE id = %s
                    ''',
                    (str(content_id),),
                )
                row = cursor.fetchone()

                if not row:
                    return Response(
                        {"detail": "content not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                return Response(
                    {
                        "id": str(row[0]),
                        "user_id": row[1],
                        "original_text": row[2],
                        "normalized_text": row[3],
                        "status": row[4],
                        "final_decision": row[5],
                        "scores": row[6],
                        "reason": row[7],
                        "created_at": row[8],
                        "updated_at": row[9],
                    }
                )
        finally:
            conn.close()
