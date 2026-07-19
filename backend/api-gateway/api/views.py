import uuid

import psycopg2
from django.conf import settings
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from moderation_common.events import EventProducer

from .serializers import LoginSerializer, RegisterSerializer


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
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "api-gateway"})


def user_response(user):
    return {
        "id": user.id,
        "username": user.get_username(),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
    }


class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrf_token": get_token(request._request)})


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request._request, user)

        return Response(
            {
                "user": user_response(user),
                "csrf_token": get_token(request._request),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request._request, user)

        return Response(
            {
                "user": user_response(user),
                "csrf_token": get_token(request._request),
            },
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request._request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": user_response(request.user)})


class ContentCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = '''
            SELECT id, user_id, original_text, status, final_decision,
                   scores, reason, created_at, updated_at
            FROM content_items
        '''
        params = []

        if not request.user.is_staff:
            query += " WHERE user_id = %s"
            params.append(request.user.get_username())

        query += " ORDER BY created_at DESC LIMIT 50"

        conn = connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
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
        user_id = request.user.get_username()
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
    permission_classes = [IsAuthenticated]

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

                if not request.user.is_staff and row[1] != request.user.get_username():
                    return Response(
                        {"detail": "You do not have permission to view this content."},
                        status=status.HTTP_403_FORBIDDEN,
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
