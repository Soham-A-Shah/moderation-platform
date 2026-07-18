FROM python:3.11-slim
WORKDIR /app

COPY common /common
RUN pip install --no-cache-dir /common

COPY backend/services/ml-inference-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/ml-inference-service .
CMD ["python", "main.py"]
