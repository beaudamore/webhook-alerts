FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/beaudamore/webhook-alerts" \
    org.opencontainers.image.description="Open WebUI alert webhook forwarder." \
    org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
