FROM python:3.11-slim
WORKDIR /app

COPY common /common
RUN pip install --no-cache-dir /common

COPY backend/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/api-gateway .
EXPOSE 8000

CMD ["sh", "entrypoint.sh"]
