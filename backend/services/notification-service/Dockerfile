FROM python:3.11-slim
WORKDIR /app

COPY common /common
RUN pip install --no-cache-dir /common

COPY backend/services/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/notification-service .
CMD ["python", "main.py"]
